"""
🧿 pupyl

Pupyl is a really fast image search library which you
can index your own (millions of) images and find similar
images in milliseconds.
"""
import os
import json
import concurrent.futures

from embeddings.features import Extractors, Characteristics
from storage.database import ImageDatabase
from indexer.facets import Index


class PupylImageSearch:
    """
    Encapsulates every aspect of pupyl, from feature extraction
    to indexing and image database.
    """
    def __init__(
            self,
            data_dir,
            **kwargs
    ):
        self._data_dir = data_dir
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
                elif mode == 'w':

                    configurations = {
                        'import_images': self._import_images,
                        'characteristic': self._characteristic.name
                    }

                    json.dump(configurations, config_file)
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
        with Extractors(characteristics=self._characteristic) as extractor:

            with Index(
                    extractor.output_shape,
                    data_dir=self._data_dir
                    ) as index:

                self._index_configuration('w')

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = {
                        executor.submit(
                            extractor.extract,
                            uri_file
                        ): uri_file
                        for uri_file in extractor.scan(uri)
                    }

                    for future in concurrent.futures.as_completed(futures):
                    # for future in extractor.progress(
                    #         concurrent.futures.as_completed(futures)
                    #         ):
                    #     uri = futures[future]

                    #     self.image_database.insert(len(index), uri)

                    #     index.append(future.result())

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
