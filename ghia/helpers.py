"""Various helper functions
"""

import configparser
import re


def load_config_multiple(paths):
    """Parse and merge multiple configuration files

    :param paths: paths to the configuration files
    :type  paths: list

    :return: fused configuration dictionary
    :rtype: dict
    """
    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read(paths.split(':'))
        return {**load_config_auth(config), **load_config_rules(config)}
    except Exception:
        return None


def load_config(config_file):
    """Parse a configuration file

    :param config_file: configuration file
    :type  config_file: file

    :return: parsed configparser configuration
    :rtype: class:`configparser.ConfigParser`
    """
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read_file(config_file)
    return config


def load_config_auth(config_parser):
    """Convert an auth cfparser config into a dictionary

    :param config_parser: configparser configuration
    :type  paths: class:`configparser.ConfigParser`

    :return: configuration as a dictionary
    :rtype: dict
    """
    config = {'github': {'token': config_parser['github']['token']}}
    if config_parser.has_option('github', 'secret'):
        config['github']['secret'] = config_parser['github']['secret']
    return config


def load_config_rules(config_parser):
    """Convert a rules cfparser config into a dictionary

    :param config_parser: configparser configuration
    :type  paths: class:`configparser.ConfigParser`

    :return: configuration as a dictionary
    :rtype: dict
    """
    config = {'patterns': {}}
    for user in config_parser['patterns']:
        config['patterns'][user] = []
        for line in config_parser['patterns'][user].splitlines():
            toks = line.split(':', 1)
            if len(toks) != 2:
                continue
            config['patterns'][user].append((toks[0], re.compile(toks[1], re.IGNORECASE)))

    if config_parser.has_option('fallback', 'label'):
        config['fallback'] = {'label': config_parser['fallback']['label']}
    return config
