# mmirror
mmirror is a tool to merge two folder structures by having a preference when duplicates are encountered.

Two inputs are provided which have some overlapping data but with different quality. This method merges these two inputs. The low output contains the merge while favoring the low quality input; the high output favors the high quality input. Both output folders will have the same data just of different quality.

Imagine inputs the following inputs as arrays instead of folders.

Low: `0, 1, 2, 3, 4`

High: `2, 3, 4, 5`

That will yield the following output arrays, where the l and h prefix
correspond to which source is used.

Low: `l0, l1, l2, l3, l4, h5`

High: `l0, l1, h2, h3, h4, 5`

## Usage
`python mmirror.py [OPTIONS] SOURCE_HIGH SOURCE_LOW`

Options:
  * `--output_high DIRECTORY` The output directory for the high merge.
  * `--output_low DIRECTORY` The output directory for the low merge.
  * `-d`, `--depth INTEGER` Defines the depth at which symlinks will be created. 1 will link folders under source.
  * `--followsymlinks` Follow symbolic links in the source paths
  * `--overwritesymlinks` Overwrite symlinks in the output directory.
  * `--simulate` Simulation mode. Don't actually do anything.
  * `-v`, `--verbose INTEGER RANGE` Logging verbosity, `-vv` for very verbose.
  * `--help` Show this message and exit.

## Requirements
mmirror requires [click](http://click.pocoo.org/). It's a library to facilitate command line arguments. In retrospect, it probably wasn't a good idea to add a dependency, but I wanted to try it out. It's available via pip: `pip install click` or `pip install -r requirements.txt` if you clone the repository.
