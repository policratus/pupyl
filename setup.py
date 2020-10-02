"""Pupyl pypi package setup. """
import setuptools


with open('README.md') as readme:
    long_description = readme.read()


setuptools.setup(
    name="pupyl",
    version="0.9.0rc0",
    author="Nelson Forte",
    author_email="policratus@gmail.com",
    description="🧿 Pupyl is a really fast image search "
    "library which you can index your own (millions of) images "
    "and find similar images in millisecond.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/policratus/pupyl",
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: GNU Lesser General Public License v3.0',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6.12'
)
