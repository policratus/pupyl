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
