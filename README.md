
![pupyl](https://github.com/policratus/pupyl/raw/master/docs/pupyl.png)

![pupyl-ci](https://github.com/policratus/pupyl/workflows/pupyl-ci/badge.svg)
[![codecov](https://codecov.io/gh/policratus/pupyl/branch/master/graph/badge.svg)](https://codecov.io/gh/policratus/pupyl)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4325/badge)](https://bestpractices.coreinfrastructure.org/projects/4325)
[![anaconda](https://anaconda.org/policratus/pupyl/badges/version.svg)](https://anaconda.org/policratus/pupyl/badges/version.svg)

# pupyl - A Python Image Search Library

## 🧿 pupyl what?
The `pupyl` project (pronounced _pyoo·piel_) is a pythonic library to image search. It's intended to made easy to read, index, retrieve and maintain a complete a reverse image search engine. You can use it in your own data pipelines, web projects and wherever you find fit!

## 🎉 Getting started
### 📦 Installation
Installing `pupyl` on your environment is pretty easy:
```
# pypi
pip install pupyl
```
or
```
# anaconda
conda install pupyl
```
## 🚸 Usage
```
import tempfile

from pupyl.search import PupylImageSearch
from pupyl.web import interface


SAMPLES = 'https://github.com/policratus/pupyl' + \
    '/raw/master/samples/pupyl.txt.xz'
DATA_DIR = tempfile.gettempdir()

SEARCH = PupylImageSearch(data_dir=DATA_DIR)

SEARCH.index(SAMPLES)

🕐 Processed 12942 items

interface.serve(DATA_DIR)
```

## 📌 Dependencies
See all dependencies here: [dependencies](https://github.com/policratus/pupyl/network/dependencies).

### 🐧 Linux
Some linux distros are packaged without some essential applications to built `pupyl` dependencies. If during the installation you face errors like this:
```
error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
```
try install `C/C++` build dependencies and `python` development headers, like this:
```
# Debian/Ubuntu
sudo apt install build-essential python3-dev

# Fedora
sudo dnf install make automake gcc gcc-c++ kernel-devel python3-devel

# Redhat/CentOS
sudo yum groupinstall 'Development Tools'
sudo yum install python3-devel

# Suse/OpenSuse
zypper install -t pattern devel_basis
zypper install python3-dev

# Arch
sudo pacman -S base-devel python3-dev

# Clearlinux
sudo swupd bundle-add c-basic python-basic-dev
```

## 📝 Documentation
See a quick reference guide on the repository [wiki](https://github.com/policratus/pupyl/wiki). Complete API reference coming soon.
