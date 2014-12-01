maproulette-overpass-loader
===========================

An interactive Challenge loader script for MapRoulette - create or maintain a challenge with just an Overpass query!

AKA the **Magic MapRoulette Machine**

## Install it

You will need to install the requirements.

`pip install -r requirements.txt`

These are pretty modest but the `overpass` requirement will still fail. This is because I am lazy and have not committed the Overpass Python wrapper to PyPi yet. For now you will need to head to [its project page](https://github.com/mvexel/overpass-api-python-wrapper), clone the repo and `python setup.py install` it.

## Use it

You can invoke the Machine in two modes: **interactive** or **headless**. In interactive mode, you will be guided through the process of creating or updating the challenge. You invoke interactive mode by calling the loader without arguments: `python loader.py`.

The headless mode is useful for maintaining a challenge. It requires no user intervention so you can use it in a cron job. To use headless mode, you will need a config file. An example is in the repository. You then pass in the path to the config file as a positional argument: `python loader.py config.yaml`. In this mode, it is assumed that you are updating an existing challenge. You can override this behavior by passing `--new`: `python loader.py --new config.yaml`

Tested with Python 2.7, should work with 3.x also.

## Wish list / Contribute / File a bug

See issues.