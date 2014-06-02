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

    def __eq__(self, other):
        return self.relative_path == other.relative_path


@click.command()
@click.argument('source_high', type=click.Path(exists=True, file_okay=False,
                                               resolve_path=True))
@click.argument('source_low', type=click.Path(exists=True, file_okay=False,
                                              resolve_path=True))
@click.option('--output_high', type=click.Path(exists=False, file_okay=False,
                                               resolve_path=True),
              help='The output directory for the high merge.')
@click.option('--output_low', type=click.Path(exists=False, file_okay=False,
                                              resolve_path=True),
              help='The output directory for the low merge.')
@click.option('-d', '--depth', default=1, help='Defines the depth at which '
              'symlinks will be created. 1 will link folders under source.')
@click.option('--followsymlinks', is_flag=True,
              help='Follow symbolic links in the source paths')
@click.option('--overwritesymlinks', is_flag=True,
              help='Overwrite symlinks in the output directory.')
@click.option('--simulate', is_flag=True,
              help='Simulation mode. Don\'t actually do anything.')
@click.option('-v', '--verbose', count=True,
              help='Logging verbosity, -vv for very verbose.')
def mmirror(source_high, source_low, output_high, output_low, depth,
            followsymlinks, overwritesymlinks, simulate, verbose):
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

    To update the output directories, run with --overwritesymlinks. This will
    update the symbolic links with new values. Be careful, this should be run
    with the same depth value as the first run.
    """
    if verbose == 1:
        log.setLevel(logging.INFO)
    elif verbose != 0:
        log.setLevel(logging.DEBUG)

    # Depth must be >=1. Otherwise, the user just wants the source folder.
    if depth < 1:
        log.error('Depth must be greater than 1.')
        return

    # At least one output directory needs to be set.
    if output_high is None and output_low is None:
        log.error('At least one output directory needs to be set.')
        return

    # The two outputs can't be the same.
    if output_high == output_low:
        log.error('The two output directories can\'t be the same.')
        return

    log.info('High:        %s', source_high)
    log.info('Low:         %s', source_low)
    log.info('Output High: %s', output_high)
    log.info('Output Low:  %s', output_low)

    shigh = iterate_input(source_high, depth, followsymlinks)
    slow = iterate_input(source_low, depth, followsymlinks)
    log.debug('Dumping high source list\n%s', pformat(shigh))
    log.debug('Dumping low source list\n%s', pformat(slow))

    if output_high:
        mirror(output_high, shigh, slow, overwritesymlinks, simulate)

    if output_low:
        mirror(output_low, slow, shigh, overwritesymlinks, simulate)


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


def mirror(path, primary, secondary, overwrite, simulate):
    """Merge secondary onto primary and output the result to path.

    First, ensure the target path exists. Then merge the two lists of Folders
    together. When there are duplicates the resulting list will contain the
    object from primary. Finally, call create_output.
    """
    if not os.path.exists(path):
        log.info('Creating directory %s', path)
        if not simulate:
            os.mkdir(path)

    merged = list(primary)
    merged.extend(filter(lambda x: x not in primary, secondary))
    merged.sort(key=Folder.relative_path)
    log.debug('Dumping merged list\n%s', pformat(merged))

    create_output(path, merged, overwrite, simulate)


def create_output(base, folders, overwrite, simulate):
    """Create the output directory structure.

    At the correct level of folder items create the symlink structure. The
    folders list should be sorted by the relative path.
    """
    for f in folders:
        path = '%s/%s' % (base, f.relative_path)
        if f.at_depth:
            # This is the item that needs to be linked. If the destination does
            # not exist, link it. If it does, one of two things can happen: if
            # the destination is a link and overwritesymlinks is set, remove it
            # then link it; otherwise, do nothing.
            if os.path.exists(path):
                if os.path.islink(path) and overwrite:
                    log.debug('Linking (overwriting) %s to %s', path,
                              f.absolute_path)
                    if not simulate:
                        os.remove(path)
                        os.symlink(f.absolute_path, path)
                else:
                    log.info('Not overwriting %s', path)
            else:
                log.debug('Linking %s to %s', path, f.absolute_path)
                if not simulate:
                    os.symlink(f.absolute_path, path)
        elif not os.path.exists(path):
            log.debug('Creating directory: %s', path)
            if not simulate:
                os.mkdir(path)

if __name__ == '__main__':
    mmirror()
