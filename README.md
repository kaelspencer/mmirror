# mmirror
__mmirror__ is a tool to merge two folder structures, having a preference when encountering duplicates. The resulting merged structure uses symbolic links at a user provided depth in the directory structures.

I wrote __mmirror__ with my music in mind, but in reality it could be used to deduplicate any pair of folders. A depth parameter tells the script at which level symbolic links should be created, and any folder above it will actually be created. My music is organized as follows: `music/FLAC/The Lawrence Arms/[2014] Metropole/`. I run the script with `music/FLAC/` as the high quality input and I want the individual albums - not the artists - to be the symlink; thus, I run with a depth of 2.

The script requires two input directories. It's most useful when there are some subdirectories that are duplicates, but this is by no means necessary. Both the high and low outputs will contain the same dataset in name, the difference will be where the symlinks point for duplicates. By default __mmirror__ uses absolute paths for the symlink targets. You can use relative paths with the switch `--relative`.

Imagine the following inputs as arrays instead of folders.

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
  * `--relative` The symbolic links should be relative paths instead of absolute paths.
  * `--simulate` Simulation mode. Don't actually do anything.
  * `-v`, `--verbose INTEGER RANGE` Logging verbosity, `-vv` for very verbose.
  * `--help` Show this message and exit.

### Example
In my situation described above, I run the script from `music/`.

    python mmirror.py flac/ mp3/ --output_high high/ --output_low low/ --depth=2

This populates `music/high/` and `music/low/`.

## Requirements
__mmirror__ requires [click](http://click.pocoo.org/). It's a library to facilitate command line arguments. In retrospect, it probably wasn't a good idea to add a dependency, but I wanted to try it out. It's available via pip: `pip install click` or `pip install -r requirements.txt` if you clone the repository.
