from pytest import raises, fixture
from biicodemaps.model import Map


@fixture
def empty_map():
    '''An empty biicodemaps.model.Map.'''
    return Map()


class TestCityCreation:

    def test_works_with_full_params(self, empty_map):
        city = empty_map.create_city('A', 0, 0)
        assert (city.name, city.x, city.y) == ('A', 0, 0)

    def test_raises_error_when_empty_param(self, empty_map):
        with raises(ValueError):
            empty_map.create_city(None, 0, 0)
        with raises(ValueError):
            empty_map.create_city('', 0, 0)
        with raises(ValueError):
            empty_map.create_city('A', None, 0)
        with raises(ValueError):
            empty_map.create_city('A', 0, None)

    def test_raises_error_when_name_exists(self, empty_map):
        empty_map.create_city('A', 0, 0)
        with raises(ValueError):
            empty_map.create_city('A', 1, 1)


@fixture
def map_with_2_cities(empty_map):
    ''' A biicodemaps.model.Map with two cities (A and B) already there.'''
    empty_map.create_city('A', 0, 0)
    empty_map.create_city('B', 1, 1)
    return empty_map


class TestRoadCreation:
    def test_works_with_full_params(self, map_with_2_cities):
        road = map_with_2_cities.create_road('A', 'B')
        assert ((road.city_1.name, road.city_2.name) == ('A', 'B') or
                (road.city_1.name, road.city_2.name) == ('B', 'A'))
        assert road in road.city_1.roads and road in road.city_2.roads

    def test_raises_error_when_empty_param(self, map_with_2_cities):
        with raises(ValueError):
            map_with_2_cities.create_road(None, 'B')
        with raises(ValueError):
            map_with_2_cities.create_road('A', None)

    def test_raises_error_when_unknow_city(self, map_with_2_cities):
        with raises(ValueError):
            map_with_2_cities.create_road('unknown', 'B')
        with raises(ValueError):
            map_with_2_cities.create_road('A', 'unknown')

    def test_raises_error_when_same_city(self, map_with_2_cities):
        with raises(ValueError):
            map_with_2_cities.create_road('A', 'A')

    def test_raises_error_when_road_exists(self, map_with_2_cities):
        map_with_2_cities.create_road('A', 'B')
        with raises(ValueError):
            map_with_2_cities.create_road('B', 'A')
