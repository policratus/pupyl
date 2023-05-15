![pupyl](https://raw.githubusercontent.com/policratus/pupyl/main/docs/pupyl.png)
![pupyl-ci](https://github.com/policratus/pupyl/workflows/pupyl-ci/badge.svg)
[![codecov](https://codecov.io/gh/policratus/pupyl/branch/main/graph/badge.svg)](https://codecov.io/gh/policratus/pupyl)
[![anaconda](https://anaconda.org/policratus/pupyl/badges/version.svg)](https://anaconda.org/policratus/pupyl/badges/version.svg)
[![PyPI version](https://badge.fury.io/py/pupyl.svg)](https://badge.fury.io/py/pupyl)
[![Documentation Status](https://readthedocs.org/projects/pupyl/badge/?version=latest)](https://pupyl.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://pepy.tech/badge/pupyl)](https://pepy.tech/project/pupyl)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4325/badge)](https://bestpractices.coreinfrastructure.org/projects/4325)
[![Anaconda-Server Badge](https://anaconda.org/policratus/pupyl/badges/platforms.svg)](https://anaconda.org/policratus/pupyl)

# pupyl - A Python Image Search Library

![pupyl](https://user-images.githubusercontent.com/827563/183988738-df6451c9-cd62-43a4-8c27-9b910379a898.gif)

# Table of contents
  * [🧿 pupyl what?](#-pupyl-what)
  * [🎉 Getting started](#-getting-started)
    + [📦 Installation](#-installation)
  * [🚸 Usage](#-usage)
    + [🐚 Command line interface](#-command-line-interface)
  * [📌 Dependencies](#-dependencies)
  * [📝 Documentation](#-documentation)
  * [🖊️ Citation](#%EF%B8%8F-citation)

## 🧿 pupyl what?

The `pupyl` project (pronounced _pyoo·piel_) is a pythonic library to perform image search tasks (even over animated GIFs). It's intended to make easy reading, indexing, retrieving and maintaining a complete reverse image search engine. You can use it in your own data pipelines, web projects and wherever you find fit!

## 🎉 Getting started
### 📦 Installation
Installing `pupyl` on your environment is pretty easy:
```Shell
# pypi
pip install pupyl
```
or
```Shell
# anaconda
conda install -c policratus pupyl
```
_For installation troubleshooting, visit [troubleshooting](TROUBLESHOOTING.md)._

## 🚸 Usage

You can call `pupyl`'s objects directly from your application code. For this example, a sample database will be indexed and after that, the following image will be used as a query image (_credits_: [@dlanor_s](https://unsplash.com/@dlanor_s)):

![@dlanor_s](https://images.unsplash.com/photo-1520763185298-1b434c919102?w=970&q=80)

_`pupyl` also supports using [animated gifs](https://en.wikipedia.org/wiki/GIF#Animated_GIF) as query images and can store and retrieve it too._

```Python
from pupyl.search import PupylImageSearch
from pupyl.web import interface

SEARCH = PupylImageSearch()

SEARCH.index(
    'https://github.com/policratus/pupyl'
    '/raw/main/samples/images.tar.xz'
)

# Using, for instance, a remote image. Local images have pretty faster results.
QUERY_IMAGE = 'https://images.unsplash.com/photo-1520763185298-1b434c919102?w=224&q=70'

[*SEARCH.search(QUERY_IMAGE)]
```

_Disclaimer: the example above creates `pupyl` assets on your temporary directory. To define a non-volatile database, you should define `data_dir` parameter._

This will return:
```Python
# Here's the simplest possible result
> [486, 12, 203, 176]
```
With more information and returning image metadata from the results:
```Python
# The results with image metadata
[*SEARCH.search(QUERY_IMAGE, return_metadata=True)]
```
Now an excerpt of the (possible) return is:
```Python
[
    {
        "id": 486,
        "internal_path": "/tmp/pupyl/0/486.gif",
        "original_access_time": "2021-12-03T13:23:47",
        "original_file_name": "icegif-5690.gif",
        "original_file_size": "261K",
        "original_path": "/tmp/tmp3gdxlwr6"
    },
    {
        "id": 12,
        "internal_path": "/tmp/pupyl/0/12.gif",
        "original_access_time": "2021-12-03T13:23:46",
        "original_file_name": "roses.gif",
        "original_file_size": "1597K",
        "original_path": "/tmp/tmp3gdxlwr6"
    },
    ...
]
```
To interact visually, use the web interface:
```Python
# Opening the web interface
interface.serve()
```
A glimpse of the web interface, visualizing the results shown above:

![web](https://pupyl.readthedocs.io/en/latest/_images/pupylresults.gif)

Alternatively, you can interact with `pupyl` via command line. The same example above in CLI
terms:

### 🐚 Command line interface
```Shell
# Indexing images
pupyl --data_dir /path/to/your/data/dir index /path/to/images/

# Opening web interface
pupyl --data_dir /path/to/your/data/dir serve

# Searching using command line interface
pupyl --data_dir /path/to/your/data/dir search /path/to/query/image.ext
```

> 💡 Type `pupyl --help` to discover all the CLI's capabilities.

## 📌 Dependencies
See all dependencies here: [dependencies](https://github.com/policratus/pupyl/network/dependencies).

## 📝 Documentation
See a getting started guide and the API reference on [https://pupyl.readthedocs.io/](http://pupyl.rtfd.io/).

## 🖊️ Citation
If you use `pupyl` in your publications or projects, please cite:

```BibTeX
@misc{pupyl,
    author = {Nelson Forte de Souza Junior},
    title = {pupyl - A Python Image Search Library},
    howpublished = {\url{https://github.com/policratus/pupyl}},
    year = {2021}
}
```
