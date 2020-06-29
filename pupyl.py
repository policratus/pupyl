"""
🧿 pupyl

Pupyl is a really fast image search library which you
can index your own (millions of) images and find similar
images in milliseconds.
"""
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
            import_images=True,
            characteristic=Characteristics.LIGHTWEIGHT_REGULAR_PRECISION
    ):
        self._data_dir = data_dir
        self._import_images = import_images
        self._characteristic = characteristic

        self.image_database = ImageDatabase(
            import_images=self._import_images,
            data_dir=self._data_dir
        )

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
                for uri_file in extractor.progress(
                        extractor.scan(uri),
                        precise=True
                        ):
                    self.image_database.insert(len(index), uri_file)
                    index.append(extractor.extract(uri_file))

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
