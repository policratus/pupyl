pupyl - A Python Image Search Library
=====================================
.. toctree::
   :maxdepth: 2
   :caption: Contents:


🧿 pupyl what?
--------------
The ``pupyl`` project (pronounced *pyoo·piel*) is a pythonic library to perform image search tasks. It's intended to made easy reading, indexing, retrieving and maintaining a complete reverse image search engine. You can use it in your own data pipelines, web projects and wherever you find fit!

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

🎉 Getting started
------------------
📦 Installation
^^^^^^^^^^^^^^^
Installing ``pupyl`` on your environment is pretty easy::

    # pypi
    pip install pupyl

or::

    # anaconda
    conda install -c policratus pupyl

*For installation troubleshooting, visit* `TROUBLESHOOTING <https://github.com/policratus/pupyl/blob/master/TROUBLESHOOTING.md>`_

🚸 Usage
-----------
You can call pupyl's objects directly from your application code:

.. code-block:: Python

    from pupyl.search import PupylImageSearch
    from pupyl.web import interface
    
    SEARCH = PupylImageSearch()
    
    SEARCH.index(
        'https://github.com/policratus/pupyl'
        '/raw/master/samples/images.tar.xz'
    )
    
    interface.serve()

*Disclaimer: the example above creates* ``pupyl`` *assets on your temporary directory. To define a non-volatile database, you should define* ``data_dir`` *parameter.*

Alternatively, you can interact with ``pupyl`` via command line. The same example above in CLI
terms:

🐚 Command line interface::
^^^^^^^^^^^^^^^^^^^^^^^^^
Here some examples of how to interact with ``pupyl`` through the command line::

    # Indexing images
    pupyl --data_dir /path/to/your/data/dir index /path/to/images/
    
    # Opening web interface
    pupyl --data_dir /path/to/your/data/dir serve

> 💡 Type `pupyl --help` to discover all the CLI's capabilities.

