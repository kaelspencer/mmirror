#!/usr/bin/python
import click
import logging

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
@click.option('-v', '--verbose', count=True,
              help='Logging verbosity, -vv for very verbose.')
def mmirror(source_high, source_low, output, verbose):
    if verbose == 1:
        log.setLevel(logging.INFO)
    elif verbose != 0:
        log.setLevel(logging.DEBUG)

    log.info('High:   %s', source_high)
    log.info('Low:    %s', source_low)
    log.info('Output: %s', output)

if __name__ == '__main__':
    mmirror()
