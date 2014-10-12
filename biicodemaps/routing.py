'''
Routing services to calculate paths in maps.

'''

import itertools
from heapq import heappop, heappush


def _safe_cities(map_, origin_city_name, destination_city_name):
    origin_city = map_.city(origin_city_name)
    if not origin_city:
        raise ValueError('Unknow city: %s.' % origin_city_name)

    destination_city = map_.city(destination_city_name)
    if not destination_city:
        raise ValueError('Unknow city: %s.' % destination_city_name)

    return origin_city, destination_city


def _results(origin_city, destination_city, previous_city, cost):
    if not previous_city[destination_city]:
        if origin_city == destination_city:
            return [origin_city.name], 0
        else:
            return [], float('infinity')

    path, city = [], destination_city
    while True:
        path.insert(0, city.name)
        city = previous_city[city]
        if not city:
            break

    return path, cost[destination_city]


def shortest_path_dijkstra_original(map_,
                                    origin_city_name, destination_city_name):
    '''
    Find shortest path using Dijkstra's original algorithm.

    [http://en.wikipedia.org/wiki/Dijkstra%27s_algorithm]

    '''
    origin_city, destination_city = _safe_cities(map_, origin_city_name,
                                                 destination_city_name)
    cities = map_.cities.values()

    # Initialize data structures
    cost, previous_city, unvisited_cities = {}, {}, []
    for city in cities:
        cost[city] = 0 if city == origin_city else float('infinity')
        previous_city[city] = None
        unvisited_cities.append(city)

    # Main loop
    while unvisited_cities:
        # get unvisited city which costs the least
        city = min(unvisited_cities, key=lambda c: cost[c])

        unvisited_cities.remove(city)
        if (city == destination_city):
            break

        # update neighbours' costs
        for road in city.roads:
            neighbour_city = road.other_end(city)
            neighbour_city_new_cost = cost[city] + road.length
            if neighbour_city_new_cost < cost[neighbour_city]:
                cost[neighbour_city] = neighbour_city_new_cost
                previous_city[neighbour_city] = city

    return _results(origin_city, destination_city, previous_city, cost)


def shortest_path_dijkstra_priority_queue(map_,
                                          origin_city_name,
                                          destination_city_name):
    '''
    Find shortest path using Dijkstra's algorithm, but using a priority queue.

    [http://en.wikipedia.org/wiki/Dijkstra%27s_algorithm]

    '''
    origin_city, destination_city = _safe_cities(map_, origin_city_name,
                                                 destination_city_name)
    cities = map_.cities.values()

    # Initialize data structures
    cost, previous_city, unvisited_cities = {}, {}, PriorityQueue()
    for city in cities:
        cost[city] = 0 if city == origin_city else float('infinity')
        previous_city[city] = None
        unvisited_cities.push(city, priority=cost[city])

    # Main loop
    while unvisited_cities:
        # get unvisited city which costs the least
        city = unvisited_cities.pop()

        if (city == destination_city):
            break

        # update neighbours' costs
        for road in city.roads:
            neighbour_city = road.other_end(city)
            neighbour_city_new_cost = cost[city] + road.length
            if neighbour_city_new_cost < cost[neighbour_city]:
                cost[neighbour_city] = neighbour_city_new_cost
                previous_city[neighbour_city] = city
                unvisited_cities.push(neighbour_city,
                                      priority=cost[neighbour_city])

    return _results(origin_city, destination_city, previous_city, cost)


class PriorityQueue(object):
    '''
    A priority queue implemented on top of heapq.

    This is necessary because heapq does not have a method to change
    an item's priority, which is something we need. We take the chance to also
    improve a couple of weak points in heapq (see link below).

    [https://docs.python.org/2/library/heapq.html]
    '''
    REMOVED = '<removed>'  # marker value for "removed" entries

    def __init__(self):
        self.queue = []                   # list of entries arranged in a heap
        self.entries = {}                 # mapping from values to entries
        self.counter = itertools.count()  # unique sequence count

    def push(self, value, priority=0):
        '''Add a new value or update the priority of an existing value.'''
        if value in self.entries:
            self.remove(value)
        count = next(self.counter)
        entry = [priority, count, value]
        self.entries[value] = entry
        heappush(self.queue, entry)

    def remove(self, value):
        '''Mark an existing value as removed. Raise KeyError if not found.'''
        entry = self.entries.pop(value)
        entry[-1] = self.REMOVED

    def pop(self, ):
        '''Remove and return lowest priority value. Raise KeyError if empty.'''
        while self.queue:
            priority, count, value = heappop(self.queue)
            if value is not self.REMOVED:
                del self.entries[value]
                return value
        raise KeyError('Pop called on empty priority queue.')
