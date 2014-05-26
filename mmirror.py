#!/usr/bin/python
import click
import logging
from pprint import pformat
import os

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d: %(message)s',
    level=logging.WARNING)
log = logging.getLogger(__name__)


@click.command()
@click.argument('source_high', type=click.Path(exists=True, file_okay=False,
                                               resolve_path=True))
@click.argument('source_low', type=click.Path(exists=True, file_okay=False,
                                              resolve_path=True))
@click.argument('output', type=click.Path(exists=True, file_okay=False,
                                          writable=True, resolve_path=True))
@click.option('-d', '--depth', default=1, help='Defines the depth at which '
              'symlinks will be created. 1 will link folders under source.')
@click.option('--followsymlinks', is_flag=True,
              help='Follow symbolic links in the source paths')
@click.option('-v', '--verbose', count=True,
              help='Logging verbosity, -vv for very verbose.')
def mmirror(source_high, source_low, output, depth, followsymlinks, verbose):
    if verbose == 1:
        log.setLevel(logging.INFO)
    elif verbose != 0:
        log.setLevel(logging.DEBUG)

    # Depth must be >=1. Otherwise, the user just wants the source folder.
    if depth < 1:
        log.error('Depth must be greater than 1.')
        return

    log.info('High:   %s', source_high)
    log.info('Low:    %s', source_low)
    log.info('Output: %s', output)

    high = iterate_input(source_high, '', depth, followsymlinks)
    low = iterate_input(source_low, '', depth, followsymlinks)
    log.debug('Dumping high source object\n%s', pformat(high))
    log.debug('Dumping low source object\n%s', pformat(low))


def iterate_input(absolute, relative, depth, followsymlinks):
    result = []

    if depth > 0:
        for dir in os.listdir(absolute):
            obj = {
                'absolute': '%s/%s' % (absolute, dir),
                'relative': ('%s/%s' % (relative, dir)).lstrip('/'),
                'at_depth': depth == 1
            }

            if os.path.isdir(obj['absolute']):
                if followsymlinks or not os.path.islink(obj['absolute']):
                    result.append(obj)
                    result.extend(iterate_input(obj['absolute'],
                                                obj['relative'], depth - 1,
                                                followsymlinks))
    return result

if __name__ == '__main__':
    mmirror()
