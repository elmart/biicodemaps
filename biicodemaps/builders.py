'''
Builders to create BiiCodeMaps from text in different ways.

Two formats are supported (BCM and RET).
For each format, you can build from a string or from a file.


BCM format
----------

BCM format is of the form:

    # Comment

    [Cities]
    <city name>, <city x coordinate (km)>, <city y coordinate (km)>
    ...

    [Roads]
    <city name>, <city name>
    ...

Comments and blank lines can appear at any position.
Cities must come before roads.


RET format
--------

RET format is a "graphical" representation that can be used to:
    - describe reticular maps, also called reticles
    - specify routing problems on reticles

A reticle is a particular kind of map where:
    - cities are at positions with integer coordinates
    - cities are connected to all other adjacent cities
    - map is densely populated: there is a city at every possible
      coordinate combination, except for a few missing ones, which
      constitute "obstacles" to be avoided by path finding algorithms.

Reticles can be diagonal or not, depending on whether cities are considered
adjacent or not when moving diagonally.

In its basic form (just to describe a reticle), RET format reads like this:

   |         |
   |  xxx    |
   |         |
   |         |
   |    o    |
   |         |
   | x       |
   | xx      |
   |         |

Where bars delimit rows, blanks are nodes (cities), connected to all adjacent
nodes, x's are "missing" nodes (obstacles from a routing algorithm perspective),
and o marks the origin for coordinates. If no o is supplied, bottom left
corner is chosen by default.

With some more additions (to specify a routing problem), RET format becomes:

   |         |
   |  xxx    |
   |       $ |
   |       @ |
   |    o @  |
   |     @   |
   | x  @    |
   | xx@     |
   |#@@      |

Where # and $ stand for the start and end nodes, and @ symbols conform to the
expected resulting path. We could also leave out the @'s if we only want to
state a problem and ask for the answer. The full form (including expected
resulting path) is mainly to be used with automated tests.

Note: In the usual case that there are several shortest paths, the same
algorithm will always choose the same one among them. But, if you test the same
spec against different algorithms, they can choose different ones. So, to test
different algorithms against the same spec, you can add as many @ symbols as
needed to cover all needed resulting paths.

'''

from biicodemaps.error import BiiCodeMapsError
from biicodemaps.model import Map


class BCMStreamMapBuilder(object):
    '''A builder that constructs a map from a BCM format stream.'''
    def __init__(self, stream):
        self.stream = stream

    def build(self):
        map_, state, line_number = Map(), None, 0
        for line in self.stream:
            line_number += 1
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith('[cities]'):
                state = 'reading_cities'
                continue
            if line.lower().startswith('[roads]'):
                state = 'reading_roads'
                continue
            if state == 'reading_cities':
                items = line.split(',')
                if len(items) != 3:
                    raise BiiCodeMapsError('Wrong number of items at line %s.' %
                                           line_number)
                name, x, y = items[0].strip(), items[1], items[2]
                try:
                    x = float(x)
                    y = float(y)
                except ValueError:
                    raise BiiCodeMapsError('Wrong format at line %s.' %
                                           line_number)
                map_.create_city(name, x, y)
            if state == 'reading_roads':
                items = line.split(',')
                if len(items) != 2:
                    raise BiiCodeMapsError('Wrong number of items at line %s.' %
                                           line_number)
                city_1, city_2 = items[0].strip(), items[1].strip()
                map_.create_road(city_1, city_2)
        return map_


class BCMFileMapBuilder(BCMStreamMapBuilder):
    '''A builder that constructs a map from a BCM format file.'''
    def __init__(self, file_name):
        self.file_name = file_name

    def build(self):
        with open(self.file_name) as f:
            self.stream = f
            return super(BCMFileMapBuilder, self).build()


class BCMStringMapBuilder(BCMStreamMapBuilder):
    '''A builder that constructs a map from a BCM format string.'''
    def __init__(self, string_):
        self.string_ = string_

    def build(self):
        self.stream = self.string_.splitlines()
        return super(BCMStringMapBuilder, self).build()


class RETStreamMapBuilder(object):
    '''A builder that constructs a reticle from a RET format stream.'''
    def __init__(self, stream, diagonal=True):
        self.stream = stream
        self.diagonal = diagonal

    def build(self):
        rows, columns, origin, missing, start, end, expected = self._scan()
        map_ = Map()
        for y in range(rows):
            for x in range(columns):
                if (x, y) not in missing:
                    # create city
                    self._create_city(map_, (x, y), origin)

                    # create roads to previously created cities
                    if x > 0 and (x - 1, y) not in missing:
                        self._create_road(map_, (x, y), (x - 1, y), origin)

                    if (self.diagonal and x > 0 and y > 0
                            and (x - 1, y - 1) not in missing):
                        self._create_road(map_, (x, y), (x - 1, y - 1), origin)

                    if y > 0 and (x, y - 1) not in missing:
                        self._create_road(map_, (x, y), (x, y - 1), origin)

                    if (self.diagonal and x < columns - 1 and y > 0
                            and (x + 1, y - 1) not in missing):
                        self._create_road(map_, (x, y), (x + 1, y - 1), origin)

        return (map_, {'rows': rows, 'columns': columns, 'origin': origin,
                       'missing': [self._transform_coordinates(m, origin)
                                   for m in missing],
                       'start': self._city_name(start, origin),
                       'end': self._city_name(end, origin),
                       'expected': [self._city_name(e, origin)
                                    for e in expected]})

    def _scan(self):
        '''
        Scan lines, checking lines format/length, and
        recording info needed later.
        '''
        line_number, rows, columns = 0, 0, None
        origin, start, end, missing, expected = None, None, None, [], []
        for line in self.stream:
            line_number += 1

            line = line.strip()
            if not line:
                continue

            rows += 1

            if not (line.startswith('|') and line.endswith('|')):
                raise BiiCodeMapsError('Wrong format (missing bar) at line %s.'
                                       % line_number)

            if columns is None:
                columns = len(line) - 2
            if len(line) - 2 != columns:
                raise BiiCodeMapsError('Wrong number of items at line %s.' %
                                       line_number)

            for column, character in enumerate(line[1:-1]):
                origin, start, end = self._process_position(
                    line_number, character, column, rows - 1,
                    origin, start, end, missing, expected)

        if not origin:
            origin = (0, rows - 1)  # default origin at bottom left corner

        if bool(start) != bool(end):
            raise BiiCodeMapsError('Only one of start/end specified.')

        if expected and not (start and end):
            raise BiiCodeMapsError('Start or end not specified.')

        expected.insert(0, start)
        expected.append(end)

        return rows, columns, origin, missing, start, end, expected

    def _process_position(self, line_number, character, column, row,
                          origin, start, end, missing, expected):
        character = character.lower()
        if character == ' ':
            pass
        elif character == '#':
            if not start:
                start = (column, row)
            else:
                raise BiiCodeMapsError('More than one start node.')
        elif character == '@':
            expected.append((column, row))
        elif character == '$':
            if not end:
                end = (column, row)
            else:
                raise BiiCodeMapsError('More than one end node.')
        elif character == 'o':
            if not origin:
                origin = (column, row)
            else:
                raise BiiCodeMapsError('More than one coordinates origin.')
        elif character == 'x':
            missing.append((column, row))
        else:
            raise BiiCodeMapsError('Unknown character %s at line %s col %s' %
                                   (character, line_number, column + 1))

        return origin, start, end

    def _create_city(self, map_, coords, origin):
        map_.create_city(self._city_name(coords, origin), *coords)

    def _create_road(self, map_, coords_1, coords_2, origin):
        map_.create_road(self._city_name(coords_1, origin),
                         self._city_name(coords_2, origin))

    def _transform_coordinates(self, coords, origin):
        '''
        Transform from reading coordinates to normal cartesian coordinates
        centered at origin. Note that apart from offset due to different
        origin, y axis is inverted between them (y grows downwards while
        reading, but upwards in a usual cartesian system).
        '''
        return (coords[0] - origin[0], origin[1] - coords[1])

    def _city_name(self, coords, origin):
        return (None if not coords else
                '%s:%s' % self._transform_coordinates(coords, origin))


class RETFileMapBuilder(RETStreamMapBuilder):
    '''A builder that constructs a reticle from a RET format file.'''
    def __init__(self, file_name, diagonal=True):
        self.file_name = file_name
        self.diagonal = diagonal

    def build(self):
        with open(self.file_name) as f:
            self.stream = f
            return super(RETFileMapBuilder, self).build()


class RETStringMapBuilder(RETStreamMapBuilder):
    '''A builder that constructs a reticle from a RET format string.'''
    def __init__(self, string_, diagonal=True):
        self.string_ = string_
        self.diagonal = diagonal

    def build(self):
        self.stream = self.string_.splitlines()
        return super(RETStringMapBuilder, self).build()
