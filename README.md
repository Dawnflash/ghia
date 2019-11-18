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

--------------------------
### Testing

The project contains 3 sets of tests:
* Unit tests in `tests`
* Integration tests in `tests_integration`
* Module tests in `tests_module`

Only unit tests are distributed in the package.
#### Unit tests
```bash
$ python test.py test
```
These tests use pre-recorded betamax cassettes for mocking GitHub API communication. You don't need to set any GitHub credentials to test.

To record cassettes anew, you need to be a member of the `mi-pyt-ghia` organization.
Run the following:
```bash
$ rm -f tests/fixtures/cassettes/*
$ export GITHUB_USER=<github user>
$ export GITHUB_TOKEN=<github token>
$ cd tests_environment
$ ./delete.sh && ./setup.sh
$ cd ..
$ python test.py test
```
#### Integration tests
These tests always use a live repo. To use them you need to be a member of the `mi-pyt-ghia` organization.
Run the following:
```bash
$ export GITHUB_USER=<github user>
$ export GITHUB_TOKEN=<github token>
$ cd tests_environment
$ ./delete.sh && ./setup.sh
$ cd ..
$ python -m pytest tests_integration
```
#### Module tests
These tests internally use integration tests so make sure to meet their requirements. Additionally, these tests test repo and package installs.
Run the following:
```bash
$ export GITHUB_USER=<github user>
$ export GITHUB_TOKEN=<github token>
$ export CTU_USERNAME=<CTU username>
$ export GHIA_REPO=<full URI to this repo (git@github.com:...)>
$ cd tests_environment
$ ./delete.sh && ./setup.sh
$ cd ..
$ python -m pytest tests_module
```
