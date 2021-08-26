"""
🧿 pupyl

Pupyl is a really fast image search library which you
can index your own (millions of) images and find similar
images in milliseconds.
"""
__version__ = 'v0.12.2'


import os
import json
import concurrent.futures

import numpy

from pupyl.duplex.file_io import FileIO
from pupyl.duplex.exceptions import FileIsNotImage
from pupyl.embeddings.features import Extractors, Characteristics
from pupyl.storage.database import ImageDatabase
from pupyl.indexer.facets import Index


class PupylImageSearch:
    """Encapsulates every aspects of ``pupyl``, from feature extraction
    to indexing and image storaging.
    """

    def __init__(
            self,
            data_dir=None,
            extreme_mode=True,
            **kwargs
    ):
        """Pupyl image search factory.

        Parameters
        ----------
        data_dir: str
            The directory where all assets are stored.

        extreme_mode: bool
            If should the extreme mode (faster execution but more memory
            consumption) be enabled or not.

        import_images: bool
            If images should (or was) imported into the database.

        characteristic: Characteristics
            The characteristic for feature extraction that must be used. If
            reading from an already created database, retrieves it from the
            (internal) configuration files.
        """
        self._extreme_mode = extreme_mode

        if data_dir:
            self._data_dir = data_dir
        else:
            self._data_dir = FileIO.pupyl_temp_data_dir()

        self._index_config_path = os.path.join(self._data_dir, 'index.json')

        configurations = self._index_configuration('r')

        if configurations:
            self._import_images = configurations['import_images']
            self._characteristic = Characteristics.by_name(
                configurations['characteristic']
            )

            if configurations.get('feature_size'):
                self._feature_size = configurations['feature_size']
        else:
            import_images = kwargs.get('import_images')
            characteristic = kwargs.get('characteristic')

            if import_images:
                self._import_images = import_images
            else:
                self._import_images = True

            if characteristic:
                self._characteristic = characteristic
            else:
                self._characteristic = Characteristics.\
                    HEAVYWEIGHT_HUGE_PRECISION

        self.image_database = ImageDatabase(
            import_images=self._import_images,
            data_dir=self._data_dir
        )

        if extreme_mode:
            self.extractor = Extractors(self._characteristic)

            self.indexer = Index(
                self.extractor.output_shape,
                data_dir=self._data_dir
            )

    def _index_configuration(self, mode, **kwargs):
        """Loads or saves an index configuration file, if exists.

        Parameters
        ----------
        mode (values: ('r', 'w')): str
            Defines which mode should be used over configuration
            file. 'r' is for file reading, 'w' for writing.

        feature_size: int
            The size of the current feature extraction method.

        Returns
        -------
        dict or bool:
            Returns a ``dict`` if an already saved database are found,
            containing several database configurations or ``bool`` ``True``
            if a new configuration file was created, or ``bool`` ``False`` if
            either a configuration couldn't be created or loaded.
        """
        try:
            with open(self._index_config_path, mode) as config_file:
                if mode == 'r':

                    return json.load(config_file)

                if mode == 'w':
                    feature_size = kwargs.get('feature_size')

                    configurations = {
                        'import_images': self._import_images,
                        'characteristic': self._characteristic.name,
                    }

                    if feature_size:
                        configurations['feature_size'] = feature_size

                    json.dump(configurations, config_file)

                return True
        except FileNotFoundError:
            return False

    def index(self, uri, **kwargs):
        """Performs parallel image indexing.

        Parameters
        ----------
        uri: str
            Directory or file, or http(s) location.

        check_unique: bool
            If, during the index process, imported images
            should have their unicity verified (to avoid duplicates).

        Attention
        ---------
        If ``check_unique`` is ``True``, consequentely unicity checks will be
        performed, which creates some overheads on the index process, making
        it slower.
        """
        check_unique = kwargs.get('check_unique')

        if check_unique is None:
            check_unique = False

        if self._extreme_mode:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        self.image_database.insert,
                        rank,
                        uri_from_file
                    ): rank
                    for rank, uri_from_file in self.extractor.progress(
                        enumerate(
                            self.extractor.scan_images(uri)
                        ),
                        precise=False,
                        message='Importing images:'
                    )
                }

                ranks = []

                for future in self.extractor.progress(
                    concurrent.futures.as_completed(futures),
                    precise=False,
                    message='Scanning images:'
                ):
                    ranks.append(futures[future])

            embeddings = numpy.empty((len(ranks), self.extractor.output_shape))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        self.extractor.extract,
                        self.image_database.mount_file_name(rank, 'jpg')
                    ): rank
                    for rank in ranks
                }

                for future in self.extractor.progress(
                    concurrent.futures.as_completed(futures),
                    precise=False,
                    message='Extracting features:'
                ):
                    try:
                        embeddings[futures[future]] = future.result()
                    except FileIsNotImage:
                        embeddings[futures[future]] = numpy.full(
                            self.extractor.output_shape, 255.
                        )

            for embedding in self.extractor.progress(
                embeddings,
                precise=True,
                message='Indexing features:'
            ):
                self.indexer.append(embedding, check_unique=check_unique)

            self.indexer.flush()

            self._index_configuration(
                'w', feature_size=self.extractor.output_shape
            )

        else:
            with Extractors(
                characteristics=self._characteristic,
                extreme_mode=self._extreme_mode
            ) as extractor:
                with Index(
                    extractor.output_shape, data_dir=self._data_dir
                ) as indexer:
                    for rank, uri_from_file in extractor.progress(
                        enumerate(
                            extractor.scan_images(uri)
                        ),
                        precise=False,
                        message='Indexing images:'
                    ):
                        self.image_database.insert(rank, uri_from_file)

                        embedding = extractor.extract(
                            self.image_database.mount_file_name(rank, 'jpg')
                        )

                        indexer.append(embedding, check_unique=check_unique)

                    self._index_configuration(
                        'w', feature_size=extractor.output_shape
                    )

    def search(self, query, top=4, return_metadata=False):
        """Executes the search for a similar image throughout the database
        based on the ``query`` image.

        Parameters
        ----------
        query: str
            URI of a image to be used as query.

        top: int
            How many results should be returned from the search process.

        return_metadata: bool
            If the image results metadata should also be returned.

        Yields
        ------
        int or dict:
            Respectively describing the image index identification that is
            decresingly (ordered) similar from the query image or a ``dict``
            with metadata information about this images (case when
            ``return_metadata=True``).
        """
        if self._extreme_mode:
            for result in self.indexer.search(
                self.extractor.extract(query),
                results=top
            ):
                yield self.image_database.load_image_metadata(result) \
                    if return_metadata else result
        else:
            with Extractors(
                characteristics=self._characteristic,
                extreme_mode=self._extreme_mode
            ) as extractor:
                with Index(
                    extractor.output_shape, data_dir=self._data_dir
                ) as indexer:
                    for result in indexer.search(
                        extractor.extract(query),
                        results=top
                    ):
                        yield self.image_database.load_image_metadata(result) \
                            if return_metadata else result
