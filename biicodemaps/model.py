'''
Domain model.

Map objects act as a factory for other domain objects. This is, all object
creation should go through them.

Regarding roads, we could have chosen to get rid of them, and have instead a
neighbour_cities attribute in each city. We have decided for roads to stay, for
two reasons:

    - Extensibility: We could easily add Road attributes (like maximum speed,
      for example) in the future.

    - Speed: We keep a (redundant) list of roads in the map, to be able to
      quickly export model data to external formats, without having to traverse
      cities to extract road info.

'''

import math
from biicodemaps.error import BiiCodeMapsError


class City(object):
    '''A city with a name and a location in cartesian coordinates.

    Attrs:
        name
        x     Horizontal coordinate
        y     Vertical coordinate
    '''
    def __init__(self, name, x, y):
        '''City constructor.

        Users should not directly instantiate this class.
        Use Map.create_city instead.
        '''
        if not name:
            raise BiiCodeMapsError('Empty name')
        if x is None:
            raise BiiCodeMapsError('Empty x')
        if y is None:
            raise BiiCodeMapsError('Empty y')
        self.name = name
        self.x = x
        self.y = y
        self._roads = []

    @property
    def roads(self):
        '''The roads this city is connected to.'''
        return self._roads

    def _add_road(self, road):
        self._roads.append(road)

    def has_road_to(self, city):
        for road in self.roads:
            if road.city_1 is city or road.city_2 is city:
                return True
        return False


class Road(object):
    '''A bidirectional road between cities.

    Attrs:
        city_1
        city_2
        length
    '''
    def __init__(self, city_1, city_2):
        '''Road constructor.

        Users should not directly instantiate this class.
        Use Map.create_road instead.
        '''
        if city_1 is city_2:
            raise BiiCodeMapsError('Cities cannot be the same: %s' %
                                   city_1.name)

        if city_1.has_road_to(city_2):
            raise BiiCodeMapsError('Road already exists')

        self._city_1 = city_1
        self._city_2 = city_2
        city_1._add_road(self)
        city_2._add_road(self)

    @property
    def city_1(self):
        return self._city_1

    @property
    def city_2(self):
        return self._city_2

    @property
    def length(self):
        return math.sqrt((self.city_1.x - self.city_2.x) ** 2 +
                         (self.city_1.y - self.city_2.y) ** 2)

    def other_end(self, city):
        '''Return the other end of this road that is not the passed city.'''
        if city == self.city_1:
            return self.city_2
        if city == self.city_2:
            return self.city_1
        raise BiiCodeMapsError('City %s does not belong to road' % city.name)


class Map(object):
    '''A map made of cities and bidirectional roads.

    It acts as a factory for other domain objects.

    Attrs:
        name   (optional)
        cities
        roads
    '''
    def __init__(self, name=None):
        self.name = name
        self._cities = {}
        self._roads = []

    @property
    def cities(self):
        return self._cities

    def city(self, name):
        try:
            return self._cities[name]
        except KeyError:
            return None

    @property
    def roads(self):
        return self._roads

    def create_city(self, name, x, y):
        if name in self._cities:
            raise BiiCodeMapsError('Name already exists')
        city = City(name, x, y)
        self._cities[name] = city
        return city

    def create_road(self, city_1_name, city_2_name):
        city_1 = self.city(city_1_name)
        if not city_1:
            raise BiiCodeMapsError('Unknown city %s' % city_1_name)

        city_2 = self.city(city_2_name)
        if not city_2:
            raise BiiCodeMapsError('Unknown city %s' % city_2_name)

        road = Road(city_1, city_2)
        self._roads.append(road)
        return road
