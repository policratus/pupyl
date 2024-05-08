"""
🧿 pupyl

Pupyl is a really fast image search library which you
can index your own (millions of) images and find similar
images in milliseconds.
"""
__version__ = 'v0.14.6'


import os
import json
from enum import Enum
import concurrent.futures

from pupyl.indexer.facets import Index
from pupyl.duplex.file_io import FileIO
from pupyl.storage.database import ImageDatabase
from pupyl.duplex.exceptions import FileIsNotImage
from pupyl.embeddings.features import Extractors, Characteristics


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

        characteristic: Enum or int or str
            The characteristic for feature extraction that must be used. If
            reading from an already created database, retrieves it from the
            (internal) configuration files. It supports retrieval by the
            ``Characteristics`` (``enum``), by its ``name`` (``str``) or
            by its ``value`` (``int``). For more information, see
            :ref:`features:📊 features module`.

        Notes
        -----
        A ``characteristic`` defines a feature extractor, with its own
        complexity and balance between search precision and indexing speed.
        Below are the description of every possible
        ``characteristic``,
        indexing the dataset
        `<https://github.com/policratus/pupyl/raw/main/samples/images.tar.xz>`_,
        containing 594 images.

        .. list-table::
           :header-rows: 1

           * - Name
             - Value
             - Network
             - Speed (GPU)
           * - MINIMUMWEIGHT_FAST_SMALL_PRECISION
             - 1
             - MobileNet
             - 19 s
           * - LIGHTWEIGHT_FAST_SMALL_PRECISION
             - 2
             - ResNet50V2
             - 21.2 s
           * - LIGHTWEIGHT_FAST_SHORT_PRECISION
             - 3
             - ResNet101V2
             - 20.3 s
           * - LIGHTWEIGHT_QUICK_SHORT_PRECISION
             - 4
             - DenseNet169
             - 32.7 s
           * - MEDIUMWEIGHT_QUICK_GOOD_PRECISION
             - 5
             - DenseNet201
             - 31.2 s
           * - MIDDLEWEIGHT_QUICK_GOOD_PRECISION
             - 6
             - InceptionV3
             - 27 s
           * - MIDDLEWEIGHT_SLOW_GOOD_PRECISION
             - 7
             - Xception
             - 20.2 s
           * - HEAVYWEIGHT_SLOW_GOOD_PRECISION
             - 8
             - EfficientNetV2M
             - 39.3 s
           * - HEAVYWEIGHT_SLOW_HUGE_PRECISION
             - 9
             - EfficientNetV2L
             - 1min 1s

        *All the tests above were under the same circumstances and resources.*

        By default, ``pupyl`` chooses ``MINIMUMWEIGHT_FAST_SMALL_PRECISION``,
        the fastest but with not so much accuracy than
        'HEAVYWEIGHT_SLOW_HUGE_PRECISION', for instance.

        Examples
        --------
        from pupyl.search import PupylImageSearch

        # Creating a database using the extractor number 3,

        # LIGHTWEIGHT_FAST_SHORT_PRECISION, network ResNet101V2

        pupyl = PupylImageSearch(characteristic=3)

        # Creating a database with extractor 'HEAVYWEIGHT_SLOW_GOOD_PRECISION',

        # based on EfficientNetV2M

        characteristic = 'HEAVYWEIGHT_SLOW_GOOD_PRECISION'

        pupyl = PupylImageSearch(characteristic=characteristic)
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

            if isinstance(characteristic, Enum):
                self._characteristic = characteristic
            elif isinstance(characteristic, int):
                self._characteristic = Characteristics.by_value(
                    characteristic
                )
            elif isinstance(characteristic, str):
                self._characteristic = Characteristics.by_name(
                    characteristic
                )
            else:
                self._characteristic = Characteristics.\
                    MINIMUMWEIGHT_FAST_SMALL_PRECISION

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
        mode: str
            Defines which mode should be used over the configuration
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
            with open(
                self._index_config_path, mode, encoding='utf-8'
            ) as config_file:
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

            with concurrent.futures.ThreadPoolExecutor() as executor:
                try:
                    futures = {
                        executor.submit(
                            self.extractor.extract_save,
                            self.image_database.mount_file_name(
                                rank, extension='npy'
                            ),
                            self.image_database.load_image_metadata(
                                rank, filtered=['internal_path']
                            )['internal_path']
                        ): rank
                        for rank in ranks
                    }

                    _ = [
                        *self.extractor.progress(
                            concurrent.futures.as_completed(futures),
                            precise=False,
                            message='Extracting features:'
                        )
                    ]

                except IndexError as index_error:
                    raise FileIsNotImage('Please, check your input images.') \
                        from index_error

            for rank in self.extractor.progress(
                sorted(ranks),
                precise=True,
                message='Indexing features:'
            ):
                self.indexer.append(
                    self.extractor.load(
                        self.image_database.mount_file_name(
                            rank, extension='npy'
                        )
                    ),
                    check_unique=check_unique
                )

            self.indexer.flush()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                for rank in ranks:
                    executor.submit(
                        self.indexer.remove_feature_cache, rank
                    )

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

                        extractor.extract_save(
                            self.image_database.mount_file_name(
                                rank, extension='npy'
                            ),
                            self.image_database.load_image_metadata(
                                rank, filterd=['internal_path']
                            )['internal_path']
                        )

                        indexer.append(
                            extractor.load(
                                self.image_database.mount_file_name(
                                    rank, extension='npy'
                                )
                            ),
                            check_unique=check_unique)

                    self._index_configuration(
                        'w', feature_size=extractor.output_shape
                    )

    def search(
        self,
        query,
        top=4,
        return_metadata=False,
        return_distances=False
    ):
        """Executes the search for a similar image throughout the database
        based on the ``query`` image.

        Parameters
        ----------
        query: str
            URI of a image to be used as query.

        top: int (optional)(default: 4)
            How many results should be returned from the search process.

        return_metadata: bool (optional)(default: False)
            If the image results metadata should also be returned.

        return_distances: bool (optional)(default: False)
            If the method should return the distances between the ``query``
            image and other images present in the database.

        Yields
        ------
        int, dict or tuple:
            Respectively describing the image index identification that is
            decresingly (ordered) similar from the query image, a ``dict``
            with metadata information about this images (case when
            ``return_metadata=True``) or a ``tuple`` when the method
            was asked to return the distances but not the image metadata
            (case when ``return_metadata=False`` and ``return_distances=True``.
        """
        if self._extreme_mode:
            for result in self.indexer.search(
                self.extractor.extract(query),
                results=top,
                return_distances=return_distances
            ):
                if return_distances:
                    yield self.image_database.load_image_metadata(
                        result[0], distance=result[1]
                    ) if return_metadata else result
                else:
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
                        results=top,
                        return_distances=return_distances
                    ):
                        if return_distances:
                            yield self.image_database.load_image_metadata(
                                result[0], distance=result[1]
                            ) if return_metadata else result
                        else:
                            yield self.image_database.load_image_metadata(
                                result
                            ) if return_metadata else result

    def remove(self, index):
        """Removes an indexed image from the storage.

        Parameters
        ----------
        index: int
            The image to be deleted, based on ``index``
            (internal image identification).

        Example
        -------
        search.remove(12) # Will remove image with ``index`` 12 from the
        storage.
        """
        if self._extreme_mode:
            self.indexer.remove(index)
        else:
            with Extractors(
                characteristics=self._characteristic,
                extreme_mode=self._extreme_mode
            ) as extractor:
                with Index(
                    extractor.output_shape, data_dir=self._data_dir
                ) as indexer:
                    indexer.remove(index)

        self.image_database.remove(index)
