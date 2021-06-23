🔰 Getting started
===================

.. _installation:

🛬 Installation
################
The installation process for ``pupyl`` is pretty easy. Using your preferred (or
even not knowing what is a)
`python virtual environment <https://docs.python.org/3.8/tutorial/venv.html>`_,
you just need to issue:

*Installing from* `pypi <https://pypi.org/project/pupyl/>`_:

.. code-block:: shell

    pip install pupyl

*Installing from* `anaconda <https://anaconda.org/policratus/pupyl>`_:

.. code-block:: shell

    conda install -c policratus pupyl

*Installing manually from* `github <https://github.com/policratus/pupyl>`_:

.. code-block:: shell

    git clone git@github.com:policratus/pupyl.git
    cd pupyl
    python setup.py install

.. _indexing:

📇 Indexing
############
After :ref:`installing <installation>`, the next step that you need is to
index your own images (preferably lots of images). ``pupyl`` supports several
ways to import and index images, but the most notably are
*from a local directory*, *from a local or remote references inside a text file*,
same as before but *from zip, bzip2, gzip, lzma compressed files*,
*from local or remote tar files containing text files referencing images* or
even *compressed tar files (using the already mentioned compression methods)
containing images itself or text files referencing images*. So, let's see every
possible way of doing this. Before we begin, first instantiate ``pupyl``
wrapper class:

.. code-block:: python

    import os

    from pupyl.search import PupylImageSearch

    # This will create pupyl database on the current directory, inside a
    # directory called 'pupyl'
    PUPYL = PupylImageSearch(data_dir=os.path.join(os.curdir, 'pupyl'))

Now, let's discuss each way of importing images:

* **From a local directory**: ``pupyl`` can look for images inside a starting
  directory, extract metadata from each image and recursively tries to find new
  images on sub-directories indefinitely (or until this search exhausts).
  So, suppose that exists a directory called ``images`` containing images
  inside it (and with several sub-directories also containing images). To index
  it, just run the :meth:`pupyl.search.PupylImageSearch.index` method:

  .. code-block:: python

      PUPYL.index(os.path.join('path', 'to', 'your', 'images'))

  having as a possible result the following:

  .. code-block:: shell

      🕛 Importing images: 709 items.
      Indexing images: 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦 67%

* **From a (remote or local) compressed tar file (images within)**: Another
  example is using a ``tar`` file with a lot of images inside it. ``pupyl``
  smart scanner infers the location type (and compression algorithm) and can
  index directly. For instance, using the same method
  :meth:`pupyl.search.PupylImageSearch.index`:

  .. code-block:: python

      PUPYL.index(
        'https://github.com/policratus/pupyl'
        '/raw/master/samples/images.tar.xz'
      )

  where this method also supports ``http`` protocol. For local files, same
  syntax:

  .. code-block:: python

      PUPYL.index(os.path.join('path', 'to, 'your', 'images.tar.xz'))

  , where both cases above uses the ``lzma`` algorithm, but it would be a
  ``tar.zip``, ``tar.gzip``, ``tar.bzip2`` or simply a ``tar`` container.

* **From (compressed or not) text files with references to images**: Sometimes,
  images takes too much of storage devices and you just need to have the
  references (or `URIs
  <https://en.wikipedia.org/wiki/Uniform_Resource_Identifier>`_). For example,
  consider the following `text file <https://en.wikipedia.org/wiki/Text_file>`_:

  .. code-block:: shell
      :linenos:

      http://www.norfolkmills.co.uk/images/Hardingham%20turbine%20Aug1965.jpg
      http://farm4.static.flickr.com/3161/2815856063_0ba82bed8a.jpg
      http://farm1.static.flickr.com/179/456107224_81f6430266.jpg
      http://farm4.static.flickr.com/3603/3569845078_ffebb00ec0.jpg
      http://farm4.static.flickr.com/3286/2945310084_ac9fdf53fa.jpg
      http://farm2.static.flickr.com/1361/816405038_030f573b86.jpg
      http://cimg2.163.com/catchpic/4/48/4823CF83B0B0D7F52BA1B80A9910D59C.jpg
      http://farm1.static.flickr.com/196/504807098_a11aff3acc.jpg
      ...

  therefore, to read the file above and resolve its references (suppose that the
  file is called ``images.txt``):

  .. code-block:: python

      PUPYL.index(os.path.join('path', 'to', 'your', 'images.txt'))

  If the file above is compressed with the already mentioned algorithms (
  ``zip``, ``gzip``, ``lzma``, ``bzip2``), same thing:

  .. code-block:: python

      # For instance, compressed with bzip2
      PUPYL.index(os.path.join('path', 'to', 'your', 'images.txt.bz2'))

  This method also supports remote files and it goes like this:

  .. code-block:: python

      # For instance, remote compressed file with gzip
      PUPYL.index('http://domain.com/images/image_references.gz')

After indexing some images, the next step is :ref:`searching <searching>`.

.. _searching:

🔭 Searching
#############
Now that you already :ref:`installed <installation>` ``pupyl`` and
:ref:`indexed <indexing>` your own images, it's time to do some searches. For
this example, please consider the following sample (``lzma`` compressed) remote
``tar`` file containing images:
`<https://github.com/policratus/pupyl/raw/master/samples/images.tar.xz>`_. It
contains 709 ``jpg`` images (stored at ``pupyl``
`github <https://github.com/policratus/pupyl>`_ repository). The
example below will create ``pupyl`` database on your home folder, inside a
directory called ``pupyl``:

.. code-block:: python

      import os
      from pathlib import Path

      from pupyl.search import PupylImageSearch

      PUPYL = PupylImageSearch(os.path.join(Path.home(), 'pupyl'))

      PUPYL.index(
          'https://github.com/policratus/pupyl'
          '/raw/master/samples/images.tar.xz'
      )

Searching is pretty simple, just needing to pick an image (local or remote) URI
as a query image (an image that you want to search inside the database to look
for other similar images). For this example, consider this beautiful image by
`@dlanor_s <https://unsplash.com/@dlanor_s>`_ (taken from
`Unsplash <https://unsplash.com/>`_):

.. image::
    https://images.unsplash.com/photo-1520763185298-1b434c919102?w=840&q=80
    :alt: Copyright @dlanor_s

Hence, to search the image above on the already indexed sample database, just
use the :meth:`pupyl.search.PupylImageSearch.search` method:

.. code-block:: python

    QUERY_IMAGE = 'https://images.unsplash.com/photo-1520763185298-1b434c919102'
    [*PUPYL.search(QUERY_IMAGE)]

    # Here's the simplest result
    [427, 473, 129, 346]

, which will yield image ``ids`` regarding the most similar images inside the
database. If you want a more detailed result, just set the parameter
``return_metadata`` to ``True``. For instance:

.. code-block:: python

    [*PUPYL.search(QUERY_IMAGE, return_metadata=True)]

    # The results with image metadata
    [{'original_file_name': '4240609837_2a679c2d59.jpg',
     'original_path': '/tmp/tmpyrmpbshx',
     'original_file_size': '127K',
     'original_access_time': '2021-06-17T15:14:19',
     'id': 427},
    {'original_file_name': '27690205_216ccaac66.jpg',
     'original_path': '/tmp/tmpyrmpbshx',
     'original_file_size': '52K',
     'original_access_time': '2021-06-17T15:14:18',
     'id': 473},
    {'original_file_name': '405530418_3d186f2a26.jpg',
     'original_path': '/tmp/tmpyrmpbshx',
     'original_file_size': '82K',
     'original_access_time': '2021-06-17T15:14:18',
     'id': 129},
    {'original_file_name': '4176670899_7633d38542.jpg',
     'original_path': '/tmp/tmpyrmpbshx',
     'original_file_size': '124K',
     'original_access_time': '2021-06-17T15:14:19',
     'id': 346}]

.. _cli:

🦪 Command line interface
##########################
Do you want to use ``pupyl`` like any another command line tool?
It's possible! The ``pupyl`` command line interface (CLI) exposes most of the
internal package behaviors and features to your preferred terminal emulator.
To use it, you must first :ref:`install <installation>` the library. After that,
just call ``pupyl`` (or ``pupyl -h``) see the arguments:

.. code-block::

    usage: pupyl [-h] [--data_dir DATA_DIR] {index,serve} ...

    🧿 Manage pupyl CLI arguments.

    pupyl is a really fast image search library which you can index your own
    (millions of) images and find similar images in milliseconds.

    positional arguments:
    {index,serve}
    index              indexes images into database
    serve              creates a web service to interact with database

    optional arguments:
    -h, --help           show this help message and exit
    --data_dir DATA_DIR  data directory for database assets

    👥 Contribute to pupyl on https://github.com/policratus/pupyl'

Indexing like described on :ref:`indexing <indexing>` section can be done like
this:

.. code-block::

    # Unix based systems
    pupyl --data_dir /path/to/your/data/dir index /path/to/images/

    # Windows systems
    pupyl -data_dir C:\path\to\your\data\dir index C:\path\to\images\

🌐 Web interface
#################

``pupyl`` also has another interface, in this case very visual. It's the web
interface, allowing you to interact with a created image database. This
interface looks like this:

.. image:: _static/pupylwebinterface.png
    :width: 840
    :alt: pupyl web interface

Hence, to use the web interface (and using the library directly):

.. code-block:: python

    import os

    from pupyl.web import interface

    interface.serve(data_dir=os.path.join('path', 'to', 'your', 'database'))

or using the :ref:`command line interface <cli>`:

.. code-block::

    # Unix based systems
    pupyl --data_dir /path/to/your/data/dir serve

    # Windows systems
    pupyl -data_dir C:\path\to\your\data\dir serve

Finally, using the same picture described on the :ref:`searching <searching>`
section and the database created on the section :ref:`indexing <indexing>`,
let's search and check the results:

.. image:: _static/pupylresults.png
    :width: 840
    :alt: pupyl web interface result

That's it! For further information about ``pupyl``, please check the
:ref:`API reference <api>`. If you want to help on the development, go to
`<https://github.com/policratus/pupyl>`_. If you want to donate, check the
`Patreon <https://www.patreon.com/pupyl>`_ page, the
`Open collective <https://opencollective.com/pupyl>`_ page or the
`LFX Crowdfunding <https://crowdfunding.lfx.linuxfoundation.org/projects/pupyl>`_.
If you had some idea for the library, please let us know on
`<https://github.com/policratus/pupyl/discussions>`_.

Please, enjoy 🧿 ``pupyl``.
