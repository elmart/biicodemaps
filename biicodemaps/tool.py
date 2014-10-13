'''
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
'''

import sys
from docopt import docopt, DocoptExit
from version import version
from biicodemaps.error import BiiCodeMapsError
from biicodemaps.builders import formats, builders
from biicodemaps.routing import algorithms
import timeit


class Task(object):
    def __init__(self, args, builder):
        self.args = args
        self.builder = builder
        self.algorithm = None
        self.silent = False

    def prepare(self):
        '''Do things that must be done just once per file/stdin.'''
        builder_result = self.builder.build()
        self.map_, self.spec = (builder_result if self.builder.format_ == 'ret'
                                else (builder_result, None))
        if self.builder.input_type == 'file':
            self.log("-- %s" % self.builder.file_name)

    def log(self, message):
        if not self.silent:
            print message

    def run(self):
        '''To be redefined by subclasses.'''
        pass


class PathTask(Task):
    def run(self):
        path, cost = algorithms[self.algorithm](self.map_,
                                                self.args['<from>'],
                                                self.args['<to>'])
        self.log('-- %s' % self.algorithm)
        self.log("Result path : %s" % path)
        self.log("Total cost  : %s" % cost)


class SolveTask(Task):
    def run(self):
        if self.builder.format_ != 'ret':
            raise DocoptExit('Solve only works with ret files.')

        self.log('-- %s' % self.algorithm)
        start, end = self.spec['start'], self.spec['end']
        if not (start and end):
            raise BiiCodeMapsError('Missing start/end in ref file.')

        path, cost = algorithms[self.algorithm](self.map_, start, end)

        self.log("Result path : %s" % path)
        self.log("Total cost  : %s" % cost)


class CheckTask(Task):
    def run(self):
        if self.builder.format_ != 'ret':
            raise DocoptExit('Check only works with ret files.')

        self.log('-- %s' % self.algorithm)
        start, end, expected = (self.spec['start'], self.spec['end'],
                                self.spec['expected'])
        if not (start and end and expected):
            raise BiiCodeMapsError('Missing start/end/expected in ret file.')

        path, cost = algorithms[self.algorithm](self.map_, start, end)

        for city in path:
            if city not in expected:
                break
        else:
            self.log('OK.')
            return
        self.log('FAILURE.')
        self.log('Algorithm result : %s' % path)
        self.log('Expected result  : %s' % expected)


def check_args(args):
    if args['--algorithm'] not in algorithms and args['--algorithm'] != 'all':
        raise DocoptExit('Unkown algorithm.')

    if args['--format'] and args['--format'] not in formats:
        raise DocoptExit('Unknown format.')

    if not args['--format'] and not args['<file>']:
        raise DocoptExit('You must specify a format if reading from stdin.')

    if args['--time-opts']:
        try:
            repeat, number = map(int, args['--time-opts'].split(':'))
        except ValueError:
            raise DocoptExit('Wrong timer options.')


def guess_format(filename):
    extension = filename[filename.rfind('.') + 1:].lower()
    return extension if extension in formats else None


tasks = []


def add_file_task(task, args, filename):
    format_ = args['--format'] or guess_format(filename)
    if not format_:
        raise DocoptExit('Unkown file format: %s.' % filename)

    builder = builders[(format_, 'file')](filename)

    tasks.append(task(args, builder))


def add_stdin_task(task, args):
    format_ = args['--format']
    builder = builders[(format_, 'stream')](sys.stdin)
    tasks.append(task(args, builder))


def get_task(args):
    return (PathTask if args['path'] else
            SolveTask if args['solve'] else
            CheckTask if args['check'] else
            None)


def show_help():
    print __doc__.strip('\n')


current_task = None


def do_task(task, algorithm, args):
    global current_task
    current_task = task
    task.algorithm = algorithm
    task.run()
    time = args['--time']
    if time:
        repeat, number = map(int, args['--time-opts'].split(':'))
        task.silent = True
        results = timeit.repeat(
            stmt='current_task.run()',
            setup='from biicodemaps.tool import current_task',
            number=number, repeat=repeat)
        print('%0.2f ms per loop in best of %s runs of %s loops'
              % (min(results) * 1000, repeat, number))
        task.silent = False


def main():
    args = docopt(__doc__, version='BiiCodeMaps %s' % version)

    if args['help']:
        show_help()
        return

    check_args(args)

    task = get_task(args)

    if not task:
        raise DocoptExit('Unknown command.')

    if args['<file>']:
        for filename in args['<file>']:
            add_file_task(task, args, filename)
    else:
        add_stdin_task(task, args)

    for task in tasks:
        try:
            task.prepare()
            if args['--algorithm'] == 'all':
                for algorithm in algorithms:
                    try:
                        do_task(task, algorithm, args)
                    except BiiCodeMapsError, e:
                        print e.message
            else:
                do_task(task, args['--algorithm'], args)
        except BiiCodeMapsError, e:
            print e.message


if __name__ == '__main__':
    main()
