from math import sqrt
from pytest import fixture, mark
from biicodemaps.model import Map
from biicodemaps.builders import RETStringMapBuilder
from biicodemaps.routing import (shortest_path_dijkstra_original,
                                 shortest_path_dijkstra_priority_queue,
                                 shortest_path_a_star)


algorithms = [shortest_path_dijkstra_original,
              shortest_path_dijkstra_priority_queue,
              shortest_path_a_star]


ret_specs = [
    '''
    |           |
    |$          |
    |@@         |
    | @@        |
    |  @@       |
    |   @@o     |
    |    @@     |
    |     @@    |
    |xxxxxx@    |
    | @@@@@     |
    |#@@@@      |

    ''',
    '''
    |         x$|
    |         x@|
    |    @@@@@@ |
    |   @@@@@@  |
    |  @x       |
    |  @x o     |
    |  @xxxxxxxx|
    |   @@@     |
    |xxxxxx@    |
    | @@@@@     |
    |#@@@@      |

    '''
]


@fixture
def trivial_cases_map(scope='module'):
    '''A small map to test trivial cases.'''
    map_ = Map()
    map_.create_city('A', 0, 0)
    map_.create_city('B', 1, 1)
    map_.create_city('C', 5, 5)
    map_.create_road('A', 'B')
    return map_


@fixture(scope='module', params=ret_specs)
def ret_spec(request):
    '''A (map_, spec) pair built from a ret document.'''
    return RETStringMapBuilder(request.param).build()


@mark.parametrize('algorithm', algorithms)
def test_trivial_cases(algorithm, trivial_cases_map):
    assert algorithm(trivial_cases_map, 'A', 'A') == (['A'], 0)
    assert algorithm(trivial_cases_map, 'A', 'C') == ([], float('infinity'))
    assert algorithm(trivial_cases_map, 'A', 'B') == (['A', 'B'], sqrt(2))


@mark.parametrize('algorithm', algorithms)
def test_ret_spec_case(algorithm, ret_spec):
    map_, spec = ret_spec
    path, cost = algorithm(map_, spec['start'], spec['end'])
    for city_name in path:
        assert city_name in spec['expected']
