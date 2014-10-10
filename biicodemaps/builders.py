'''
Builders to create BiiCodeMaps from different sources in BCM format.

BCM format for input data is defined this way:

    # Comment

    [Cities]
    <city name>, <city x coordinate (km)>, <city y coordinate (km)>
    ...

    [Roads]
    <city name>, <city name>
    ...

Comments and blank lines can appear at any position.
Cities must come before roads.

'''

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
                    raise Exception('Wrong number of items at line %s.' %
                                    line_number)
                name, x, y = items[0].strip(), items[1], items[2]
                try:
                    x = float(x)
                    y = float(y)
                except ValueError:
                    raise Exception('Wrong format at line %s.' % line_number)
                map_.create_city(name, x, y)
            if state == 'reading_roads':
                items = line.split(',')
                if len(items) != 2:
                    raise Exception('Wrong number of items at line %s.' %
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
