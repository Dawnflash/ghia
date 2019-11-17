#! /usr/bin/env python
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='ghia_zahumada',
    version='0.3',
    description='Assigns GitHub issues to people (cli batch/webhook)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='github, issues, webhook, cli',
    author='Adam Zahumensky',
    author_email='zahumada@fit.cvut.cz',
    license='MIT License',
    url='https://github.com/Dawnflash/ghia',
    packages=['ghia'],
    package_data={'ghia': ['templates/*.html', 'tests']},
    entry_points={
        'console_scripts': [
            'ghia = ghia.cli:cli',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Framework :: Flask',
        'Environment :: Console',
        'Environment :: Web Environment',
    ],
    install_requires=['Flask', 'click', 'requests'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'betamax'],
    zip_safe=False,
)
