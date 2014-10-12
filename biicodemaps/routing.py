'''
Routing services to calculate paths in maps.

'''


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
