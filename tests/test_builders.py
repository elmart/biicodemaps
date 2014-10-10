import os
from biicodemaps.builders import BCMStringMapBuilder, BCMFileMapBuilder


class TestBuildingFromString:
    def test_works_with_correct_input(self):
        map_ = BCMStringMapBuilder('''
                                   # A sample map

                                   [cities]
                                   A, 0.5, -1.2
                                   B, -3.2, 0.8
                                   C, 5, 5

                                   [roads]
                                   A, B
                                   B, C
                                   ''').build()
        assert len(map_.cities) == 3
        assert len(map_.roads) == 2
        city = map_.city('B')
        assert city.name == 'B' and city.x == -3.2 and city.y == 0.8
        assert len(city.roads) == 2


class TestBuildingFromFile:
    def test_loads_ok(self):
        BCMFileMapBuilder(os.path.join(os.path.dirname(__file__),
                                       'sample_map.bcm')).build()
