"""
🧿 pupyl

Pupyl is a really fast image search library which you
can index your own (millions of) images and find similar
images in milliseconds.
"""
__version__ = 'v0.11.4'


import os
import json
import concurrent.futures

from pupyl.duplex.file_io import FileIO
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
            **kwargs
    ):
        """Pupyl image search factory.

        Parameters
        ----------
        data_dir: str
            The directory where all assets are stored.

        import_images: bool
            If images should (or was) imported into the database.

        characteristic: Characteristics
            The characteristic for feature extraction that must be used. If
            reading from an already created database, retrieves it from the
            (internal) configuration files.
        """
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
        with Extractors(
                characteristics=self._characteristic
        ) as extractor, Index(
            extractor.output_shape,
            data_dir=self._data_dir
        ) as index:

            self._index_configuration('w', feature_size=extractor.output_shape)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        self.image_database.insert,
                        rank,
                        uri_from_file
                    ): rank
                    for rank, uri_from_file in enumerate(
                        extractor.scan_images(uri)
                    )
                }

                ranks = []

                for future in extractor.progress(
                        concurrent.futures.as_completed(futures),
                        message='Importing images:'
                ):
                    ranks.append(futures[future])

                for rank in extractor.progress(
                    sorted(ranks),
                    precise=True,
                    message='Indexing images:'
                ):
                    features_tensor_name = self.image_database.\
                        mount_file_name(
                            rank,
                            'npy'
                        )

                    extractor.save_tensor(
                        extractor.extract,
                        self.image_database.mount_file_name(
                            rank,
                            'jpg'
                        ),
                        features_tensor_name
                    )

                    check_unique = kwargs.get('check_unique')

                    if check_unique is None:
                        check_unique = False

                    index.append(
                        extractor.load_tensor(
                            features_tensor_name
                        ),
                        check_unique=check_unique
                    )

                    os.remove(features_tensor_name)

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
        with Extractors(characteristics=self._characteristic) as extractor:
            with Index(
                    extractor.output_shape,
                    data_dir=self._data_dir
            ) as index:
                for result in index.search(
                        extractor.extract(query),
                        results=top
                ):
                    if return_metadata:
                        yield self.image_database.load_image_metadata(result)
                    else:
                        yield result
