maproulette-overpass-loader
===========================

An interactive Challenge loader script for MapRoulette - create or maintain a challenge with just an Overpass query!

AKA the **Magic MapRoulette Machine**

## Use it

You will need to install the requirements.

`pip install -r requirements.txt`

These are pretty modest but the `overpass` requirement will still fail. This is because I am lazy and have not committed the Overpass Python wrapper to PyPi yet. For now you will need to head to [its project page](https://github.com/mvexel/overpass-api-python-wrapper), clone the repo and `python setup.py install` it.

Once all that is done, you can invoke the Machine with `python loader.py`. There are no arguments.

Tested with Python 2.7, should work with 3.x also.

## Wish list / Contribute / File a bug

See issues.