# BiiCodeMaps

A small utility to deal with routing problems on maps.

Maps consist of cities and roads, where cities have cartesian coordinates,
and roads connect two cities bidirectionally.
Roads are supposed straight.

BiiCodeMaps supports:
- Different formats for input files describing maps.
- Several algorithms to compute shortest paths.
- Showing time statistics to compare algorithms.
- Checking algorithms against expected results included in files.


## Usage
```
BiiCodeMaps: Map routing problems for the masses.

Usage:
    bcm path [options] <from> <to> ([-] | <file>...)
    bcm solve [options] ([-] | <file>...)
    bcm check [options] ([-] | <file>...)
    bcm help

Options:
    -a <alg> --algorithm=<alg>       Algorithm to be used. One of:
                                     * a-star  A*
                                     * dij-o   Dijkstra's original
                                     * dij-pq  Dijkstra with priority queue
                                     [default: a-star]

    -f <format> --format=<format>    Input data format (bcm or ret).
                                     Can be guessed from file extension if any.
                                     Should be specified if reading from stdin.

    -t --time                        Report elapsed time for each task.

    --time-opts <time_opts>          Arguments for timeit, in the form
                                     '<repeat>:<number>'.
                                     [default: 3:100]

    -h --help     Show this help.
    -v --version  Show version.

Commands:
    path   Compute shortest path between passed nodes.
           Graph info is taken from file.

    solve  Compute shortest path problem specified in file.
           Graph info and start & end nodes are taken from file.
           [ref files only]

    check  Compute and check shortest path problem specified on file.
           Graph info, start & end nodes, and expected results are taken
           from file.
           [ret files only]

    help   Show this help.
```

## Input data formats

### BCM format

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


### RET format

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
```
   |         |
   |  xxx    |
   |         |
   |         |
   |    o    |
   |         |
   | x       |
   | xx      |
   |         |
```
Where bars delimit rows, blanks are nodes (cities), connected to all adjacent
nodes, x's are "missing" nodes (obstacles from a routing algorithm perspective),
and o marks the origin for coordinates. If no o is supplied, bottom left
corner is chosen by default.

With some more additions (to specify a routing problem), RET format becomes:
```
   |         |
   |  xxx    |
   |       $ |
   |       @ |
   |    o @  |
   |     @   |
   | x  @    |
   | xx@     |
   |#@@      |
```
Where # and $ stand for the start and end nodes, and @ symbols conform to the
expected resulting path. We could also leave out the @'s if we only want to
state a problem and ask for the answer. The full form (including expected
resulting path) is mainly to be used with automated tests.

Note: In the usual case that there are several shortest paths, the same
algorithm will always choose the same one among them. But, if you test the same
spec against different algorithms, they can choose different ones. So, to test
different algorithms against the same spec, you can add as many @ symbols as
needed to cover all needed resulting paths.
