"""Pupyl pypi package setup. """
import setuptools


with open('README.md') as readme:
    long_description = readme.read()


setuptools.setup(
    name="pupyl",
    version="0.10.2",
    author="Nelson Forte",
    author_email="policratus@gmail.com",
    description="🧿 Pupyl is a really fast image search "
    "library which you can index your own (millions of) images "
    "and find similar images in millisecond.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/policratus/pupyl",
    packages=setuptools.find_packages(),
    install_requires=[
        'tensorflow>=2.3.0',
        'annoy>=1.17.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        (
            'License :: OSI Approved :: '
            'GNU Lesser General Public License v3 (LGPLv3)'
        ),
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Image Recognition'
    ],
    python_requires='>=3.6.12'
)
