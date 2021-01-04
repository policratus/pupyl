"""
🧿 pupyl

Pupyl is a really fast image search library which you
can index your own (millions of) images and find similar
images in milliseconds.
"""
__version__ = 'v0.10.5'


import os
import json
import concurrent.futures

from pupyl.duplex.file_io import FileIO
from pupyl.embeddings.features import Extractors, Characteristics
from pupyl.storage.database import ImageDatabase
from pupyl.indexer.facets import Index


class PupylImageSearch:
    """
    Encapsulates every aspect of pupyl, from feature extraction
    to indexing and image database.
    """

    def __init__(
            self,
            data_dir=None,
            **kwargs
    ):
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
        """
        Load or save an index configuration file, if exists.

        Parameters
        ----------
        mode (values: ('r', 'w')): str
            Defines which mode should be used over configuration
            file. 'r' is for file reading, 'w' for writing.

        feature_size(optional): int
            The size of current feature extraction method.
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
        """
        Performs image indexing.

        Parameters
        ----------
        uri: str
            Directory or file, or http(s) location.

        **check_unique (optional): bool
            If, during the index process, imported images
            should have their unicity verified (to avoid duplicates).
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
                        message='Importing images.'
                ):
                    ranks.append(futures[future])

                for rank in extractor.progress(
                    sorted(ranks),
                    precise=True,
                    message='Indexing images.'
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

    def search(self, query, top=4):
        """
        Executes the search for a created database

        Parameters
        ----------
        query: str
            URI of a image to query

        top (optional)(default: 4): int
            How many results should be returned.
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
                    yield result
