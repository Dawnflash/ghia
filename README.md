# GitHub Issue Assigner (GHIA)

## MI-PYT assignment
### Links
>Assignment: https://github.com/cvut/ghia \
>Demo webapp: http://ghia.dawnflash.cz

Author: Adam Zahumensky <zahumada@fit.cvut.cz>

--------------------------
### Flask mode
In this mode the app acts as a webhook receiver for Github

```bash
$ GHIA_CONFIG=<path_a, path_b, ...> FLASK_APP=ghia.py flask run
```
>GHIA_DRYRUN: set dry run \
>GHIA_STRATEGY: switch strategy <set|change> (default: append)

### CLI mode
Batch-process all issues in a single run
```bash
$ python -m ghia --help
```
