![pupyl](docs/pupyl.png)
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

You can call pupyl's objects directly from your application code:

```Python
from pupyl.search import PupylImageSearch
from pupyl.web import interface

SEARCH = PupylImageSearch()

SEARCH.index(
    'https://github.com/policratus/pupyl'
    '/raw/master/samples/images.tar.xz'
)

interface.serve()
```
_Disclaimer: the example above creates `pupyl` assets on your temporary directory. To define a non-volatile database, you should define `data_dir` parameter._

Alternatively, you can interact with pupyl via command line. The same example above in CLI
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
See a quick reference guide on the repository [wiki](https://github.com/policratus/pupyl/wiki). Complete API reference coming soon.

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
