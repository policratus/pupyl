# Troubleshooting
## Installation
### 🐧 Linux
Some linux distros are packaged without some essential applications to built `pupyl` dependencies. If during the installation you face errors like this:
```shell
error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
```
try install `C/C++` build dependencies and `python` development headers, like this:
```shell
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

### 🪟 Windows
When installing `pupyl` on Windows, a `C++` compiler must be installed on the system. If there isn't a suitable compiler, you will probably see the error below.

```shell
error: Microsoft Visual C++ 14.0 is required. Get it with "Build Tools for Visual Studio": https://visualstudio.microsoft.com/downloads
```

Install the `C++` compiler donwloading it from [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

### 🍏 macOS
`pupyl` also needs a `C++` compiler on macOS, which `clang` is usually installed by default. If you still face some problems, try to define the compilers' path before:

```shell
export CC=/usr/bin/clang
export CXX=/usr/bin/clang++
```

## I have a NVIDIA© GPU but `pupyl` isn't using it.
As `pupyl` relies on [tensorflow](https://www.tensorflow.org/) for [GPU](https://en.wikipedia.org/wiki/Graphics_processing_unit) integration and it relies consequentely on [CUDA](https://developer.nvidia.com/cuda-zone), you should check which `CUDA` version the current stable `tensorflow` version is dependent. `pupyl` has the compromise to always use the latest stable of `tensorflow`.

`CUDA` and NVIDIA© drivers are platform dependent, so it's sufficiently complex to not be part of `pupyl` installation. Please, follow the installation guides:
* For **Linux** distros: [NVIDIA CUDA Installation Guide for Linux](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)
* For **Windows** platforms: [CUDA Installation Guide for Microsoft Windows](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)
