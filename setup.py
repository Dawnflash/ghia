#! /usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='ghia_zahumada',
    version='0.3',
    description='Assigns GitHub issues to people (cli batch/webhook)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Adam Zahumensky',
    author_email='zahumada@fit.cvut.cz',
    license='MIT License',
    url='https://github.com/Dawnflash/ghia',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ghia = ghia.cli:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    install_requires=['Flask', 'click', 'requests'],
    zip_safe=False,
)
