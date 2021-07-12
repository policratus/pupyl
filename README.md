![pupyl](https://raw.githubusercontent.com/policratus/pupyl/master/docs/pupyl.png)
![pupyl-ci](https://github.com/policratus/pupyl/workflows/pupyl-ci/badge.svg)
[![codecov](https://codecov.io/gh/policratus/pupyl/branch/master/graph/badge.svg)](https://codecov.io/gh/policratus/pupyl)
[![anaconda](https://anaconda.org/policratus/pupyl/badges/version.svg)](https://anaconda.org/policratus/pupyl/badges/version.svg)
[![PyPI version](https://badge.fury.io/py/pupyl.svg)](https://badge.fury.io/py/pupyl)
[![Documentation Status](https://readthedocs.org/projects/pupyl/badge/?version=latest)](https://pupyl.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://pepy.tech/badge/pupyl)](https://pepy.tech/project/pupyl)

# pupyl - A Python Image Search Library

## 🧿 pupyl what?

The `pupyl` project (pronounced _pyoo·piel_) is a pythonic library to perform image search tasks. It's intended to made easy reading, indexing, retrieving and maintaining a complete reverse image search engine. You can use it in your own data pipelines, web projects and wherever you find fit!

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

```Python
from pupyl.search import PupylImageSearch
from pupyl.web import interface

SEARCH = PupylImageSearch()

SEARCH.index(
    'https://github.com/policratus/pupyl'
    '/raw/master/samples/images.tar.xz'
)

QUERY_IMAGE = 'https://images.unsplash.com/photo-1520763185298-1b434c919102'

[*SEARCH.search(QUERY_IMAGE)]

# Here's the simplest result
> [427, 473, 129, 346]

# The results with image metadata
[*SEARCH.search(QUERY_IMAGE, return_metadata=True)]

> [
    {
        'original_file_name': '941444733_6de664bbbf.jpg',
        'original_path': '/tmp/tmp_i42jozv',
        'original_file_size': '80K',
        'original_access_time': '2021-07-06T20:31:07',
        'id': 427
    },
    {
        'original_file_name': '2673396259_f151fbe7c1.jpg',
        'original_path': '/tmp/tmp_i42jozv',
        'original_file_size': '66K',
        'original_access_time': '2021-07-06T20:31:07',
        'id': 473
    },
    ...
  ]

# Opening the web interface
interface.serve()
```
A glimpse of the web interface, visualizing the results shown above:

![web](https://pupyl.readthedocs.io/en/latest/_images/pupylresults.png)

_Disclaimer: the example above creates `pupyl` assets on your temporary directory. To define a non-volatile database, you should define `data_dir` parameter._

Alternatively, you can interact with `pupyl` via command line. The same example above in CLI
terms:

### 🐚 Command line interface
```Shell
# Indexing images
pupyl --data_dir /path/to/your/data/dir index /path/to/images/

# Opening web interface
pupyl --data_dir /path/to/your/data/dir serve
```

> 💡 Type `pupyl --help` to discover all the CLI's capabilities.

## 📌 Dependencies
See all dependencies here: [dependencies](https://github.com/policratus/pupyl/network/dependencies).

## 📝 Documentation
See a getting start guide and the API reference on [https://pupyl.readthedocs.io/](http://pupyl.rtfd.io/).

## 🖊️ Citation
If you use `pupyl` on your publications or projects, please cite:

```BibTeX
@misc{pupyl,
    author = {Nelson Forte de Souza Junior},
    title = {pupyl},
    howpublished = {\url{https://github.com/policratus/pupyl}},
    year = {2021}
}
```
