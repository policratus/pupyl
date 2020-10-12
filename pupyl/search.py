"""
🧿 pupyl

Pupyl is a really fast image search library which you
can index your own (millions of) images and find similar
images in milliseconds.
"""
__version__ = 'v0.10.2'


import os
import json
from urllib.error import URLError
from http.client import RemoteDisconnected

from pupyl.duplex.file_io import FileIO
from pupyl.embeddings.features import Extractors, Characteristics
from pupyl.storage.database import ImageDatabase
from pupyl.indexer.facets import Index
from pupyl.duplex.exceptions import FileIsNotImage


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
                    LIGHTWEIGHT_REGULAR_PRECISION

        self.image_database = ImageDatabase(
            import_images=self._import_images,
            data_dir=self._data_dir
        )

    def _index_configuration(self, mode):
        """
        Load or save an index configuration file, if exists.

        Parameters
        ----------
        mode (values: ('r', 'w')): str
            Defines which mode should be used over configuration
            file. 'r' is for file reading, 'w' for writing.
        """
        try:
            with open(self._index_config_path, mode) as config_file:
                if mode == 'r':

                    return json.load(config_file)

                if mode == 'w':

                    configurations = {
                        'import_images': self._import_images,
                        'characteristic': self._characteristic.name
                    }

                    json.dump(configurations, config_file)

                return True
        except FileNotFoundError:
            return False

    def index(self, uri):
        """
        Performs image indexing.

        Parameters
        ----------
        uri: str
            Directory or file, or http(s) location.
        """
        with Extractors(
                characteristics=self._characteristic
        ) as extractor, Index(
            extractor.output_shape,
            data_dir=self._data_dir
        ) as index:

            self._index_configuration('w')

            for rank, uri_from_file in enumerate(
                    extractor.progress(extractor.scan(uri))
            ):
                features_tensor_name = self.image_database.mount_file_name(
                    rank,
                    'npy'
                )

                try:
                    extractor.save_tensor(
                        extractor.extract,
                        uri_from_file,
                        features_tensor_name
                    )

                    self.image_database.insert(len(index), uri_from_file)
                except (
                        URLError, FileIsNotImage,
                        RemoteDisconnected, ConnectionResetError
                ):
                    continue

                index.append(extractor.load_tensor(features_tensor_name))

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
