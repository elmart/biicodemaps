import os
from biicodemaps.builders import (BCMStringMapBuilder, BCMFileMapBuilder,
                                  RETStringMapBuilder, RETFileMapBuilder)


class TestBuildingFromBCMString:
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


class TestBuildingFromBCMFile:
    def test_loads_ok(self):
        BCMFileMapBuilder(os.path.join(os.path.dirname(__file__),
                                       'sample_map.bcm')).build()


class TestBuildingFromRETString:
    def test_diagonal(self):
        map_, spec = RETStringMapBuilder('''
                                   |           |
                                   |  o        |
                                   |     x     |
                                   |      x    |
                                   |       x   |
                                   |           |
                                   |  x        |
                                   |  x        |
                                   |  xxx      |
                                   |           |
                                   |           |
                                   ''').build()
        assert spec['origin'] == (2, 1)
        assert len(map_.cities) == 113
        assert len(map_.roads) == 363
        for coords in [(3, -1), (4, -2), (5, -3), (0, -5),
                       (0, -6), (0, -7), (1, -7), (2, -7)]:
            assert not map_.city('%s:%s' % coords)

    def test_non_diagonal(self):
        map_, spec = RETStringMapBuilder('''
                                   |           |
                                   |  o        |
                                   |     x     |
                                   |      x    |
                                   |       x   |
                                   |           |
                                   |  x        |
                                   |  x        |
                                   |  xxx      |
                                   |           |
                                   |           |
                                   ''', diagonal=False).build()
        assert spec['origin'] == (2, 1)
        assert len(map_.cities) == 113
        assert len(map_.roads) == 192
        for coords in [(3, -1), (4, -2), (5, -3), (0, -5),
                       (0, -6), (0, -7), (1, -7), (2, -7)]:
            assert not map_.city('%s:%s' % coords)


class TestBuildingFromRETFile:
    def test_loads_ok(self):
        RETFileMapBuilder(os.path.join(os.path.dirname(__file__),
                                       'sample_map.ret')).build()
