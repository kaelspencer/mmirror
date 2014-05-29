#!/usr/bin/python
import click
import logging
from pprint import pformat
import os

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d: %(message)s',
    level=logging.WARNING)
log = logging.getLogger(__name__)


class Folder(object):
    """This class represents needed information about a folder."""
    def __init__(self, absolute_path, relative_path, at_depth):
        super(Folder, self).__init__()
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.at_depth = at_depth

    def absolute_path(self):
        return self.absolute_path

    def relative_path(self):
        return self.relative_path

    def at_depth(self):
        return self.at_depth

    def __repr__(self):
        return '<%s, %s, %s>' % (self.absolute_path, self.relative_path,
                                 self.at_depth)


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
    """Create a symlinked merged directory of high and low sources.

    Two inputs are provided which have some overlapping data but with different
    quality. This method merges these two inputs. The low output contains the
    merge while favoring the low quality input; the high output favors the
    high quality input. Both output folders will have the same data just of
    different quality.

    Imagine inputs the following inputs as arrays instead of folders.
    Low: 0, 1, 2, 3, 4
    High: 2, 3, 4, 5

    That will yield the following output arrays, where the l and h prefix
    correspond to which source is used.
    Low: l0, l1, l2, l3, l4, h5
    High: l0, l1, h2, h3, h4, 5
    """
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

    shigh = iterate_input(source_high, depth, followsymlinks)
    slow = iterate_input(source_low, depth, followsymlinks)
    log.debug('Dumping high source object\n%s', pformat(shigh))
    log.debug('Dumping low source object\n%s', pformat(slow))

    dhigh, dlow = validate_output_directories(output, depth)
    log.debug('Dumping high destination object\n%s', pformat(dhigh))
    log.debug('Dumping low destination object\n%s', pformat(dlow))


def iterate_input(absolute, depth, followsymlinks, relative=''):
    """Recursively iterate through the input creating objects for merging.

    Create an object for each directory with absolute path, relative path, and
    a flag indicating whether this directory is at the target depth. This does
    not make a recursive call on directories already at depth.
    """
    result = []

    for dir in os.listdir(absolute):
        obj = Folder('%s/%s' % (absolute, dir),
                    ('%s/%s' % (relative, dir)).lstrip('/'), depth == 1)

        if os.path.isdir(obj.absolute_path):
            if followsymlinks or not os.path.islink(obj.absolute_path):
                result.append(obj)
                if not obj.at_depth:
                    result.extend(iterate_input(obj.absolute_path, depth - 1,
                                                followsymlinks,
                                                obj.relative_path))
    return result


def validate_output_directories(base, depth):
    """Ensure the output directories exist and populate object lists.

    If the output directories don't exist, create them. If they do, populate
    object lists with their contents. This will be used when generating the
    output links.
    """
    def ensure_directory(path):
        if not os.path.exists(path):
            log.info('Creating directory %s', path)
            os.mkdir(path)

    output_high = base + '/music.high'
    output_low = base + '/music.low'
    ensure_directory(base)
    ensure_directory(output_high)
    ensure_directory(output_low)

    # Iterate over the output directories. Explicitly avoid going into symlink
    # folders. That behavior could be weird.
    high = iterate_input(output_high, depth, False)
    low = iterate_input(output_low, depth, False)

    return high, low


if __name__ == '__main__':
    mmirror()
