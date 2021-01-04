"""
facets Module.

Hyperspace indexing and operations.
"""
import os
from warnings import warn as warning
from shutil import move, copyfile

from annoy import AnnoyIndex

from pupyl.indexer.exceptions import FileIsNotAnIndex, \
    IndexNotBuildYet, NoDataDirForPermanentIndex, \
    DataDirDefinedForVolatileIndex, NullTensorError, \
    TopNegativeOrZero, EmptyIndexError
from pupyl.addendum.operators import intmul
from pupyl.duplex.file_io import FileIO
from pupyl.storage.database import ImageDatabase


class Index:
    """Procedures over multidimensional spaces."""

    def __init__(self, size, data_dir=None, trees=.001, volatile=False):
        """
        Indexing tensors operations and nearest neighbours search.

        Parameters
        ----------
        size: int
            Shape of unidimensional vectors which will be indexed

        data_dir: str
            Location where to load or save the index

        trees (optional): float
            Defines the number of trees to create based on the dataset
            size. Should be a number between 0 and 1.

        volatile (optional): bool
            If the index will be temporary or not.
        """
        self._position = -1
        self._size = size
        self._data_dir = data_dir
        self._trees = trees
        self._volatile = volatile

        if self._data_dir and not self._volatile:
            if os.path.isfile(self._data_dir):
                raise OSError('data_dir parameter is not a directory')

            os.makedirs(self._data_dir, exist_ok=True)
            self._path = os.path.join(self._data_dir, self.index_name)
        elif not self._data_dir and not self._volatile:
            raise NoDataDirForPermanentIndex
        elif not self._data_dir and self._volatile:
            _temp_file = FileIO.safe_temp_file()
            self._data_dir = os.path.dirname(_temp_file)
            self._path = _temp_file

        else:
            raise DataDirDefinedForVolatileIndex

        if os.path.isfile(self._path):
            try:
                self.tree = AnnoyIndex(size, metric='angular')

                self.tree.load(self._path)

                self._is_new_index = False
            except OSError as os_error:
                raise FileIsNotAnIndex from os_error
        else:
            self.tree = AnnoyIndex(size, metric='angular')
            self._is_new_index = True

        self._image_database = ImageDatabase(
            import_images=True,
            data_dir=self._data_dir,
        )

    @property
    def size(self):
        """Getter for property size."""
        return self._size

    @property
    def path(self):
        """Getter for property path."""
        return self._path

    @property
    def index_name(self):
        """Getter for property index_name."""
        return 'pupyl.index'

    @property
    def trees(self):
        """Getter for property trees."""
        return self._trees

    @property
    def volatile(self):
        """Getter for property volatile."""
        return self._volatile

    @trees.setter
    def trees(self, trees):
        """Setter for property trees."""
        self._trees = trees

    def __enter__(self):
        """Context opening index."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context closing index."""
        if not exc_type:

            if self._is_new_index:
                self.tree.build(self.size << intmul >> self.trees)

                self.tree.save(self.path)

            self.tree.unload()

    def items(self):
        """Return the indexed items."""
        for item in range(len(self)):
            yield item

    def values(self):
        """Return the indexed values."""
        for item in self.items():
            yield self.tree.get_item_vector(item)

    def items_values(self):
        """Return tuples with all items and values."""
        for item, value in zip(self.items(), self.values()):
            yield item, value

    def __getitem__(self, position):
        """Return item at index. Supports negative slicing."""
        if position >= 0:
            return self.tree.get_item_vector(position)

        return self.tree.get_item_vector(
            len(self) - abs(position)
        )

    def refresh(self):
        """Update all information regarding index file."""
        self.tree.unload()
        self.tree.load(self.path)

    def append(self, tensor, check_unique=False):
        """
        Insert a new tensor at the end of the index.
        Be advised that this operation is linear on index size ($O(n)$).

        Parameters
        ----------
        tensor: numpy.ndarray or list
            A vector to insert into index.

        check_unique (optional, default: False): bool
            Defines if append method should verify the existence
            of a really similar tensor on the current index. In other words,
            it checks for the unicity of the value. Be advised that this check
            creates an overhead on the append process.
        """
        if sum(tensor) == 0.:
            raise NullTensorError

        if self._is_new_index:

            index_it = True

            if check_unique and len(self) > 1:

                self.tree.build(self.size << intmul >> self.trees)

                result = self.item(
                    self.index(tensor),
                    top=1,
                    distances=True
                )

                if result[1][0] <= .05:
                    warning(
                        'Tensor being indexed already exists in '
                        'the database and the check for duplicates '
                        'are on. Refusing to store again this tensor.'
                    )

                    index_it = False

                self.tree.unbuild()

            if index_it:
                self.tree.add_item(len(self), tensor)

        else:

            with Index(self.size, volatile=True, trees=self.trees) as tmp_idx:
                for value in self.values():
                    tmp_idx.append(value, check_unique)

                tmp_idx.append(tensor, check_unique)

                _temp_file = tmp_idx.path

            move(_temp_file, self.path)

            self.refresh()

    def remove(self, position):
        """
        Remove the tensor at index from the database.
        Be advised that this operation is linear on index size ($O(n)$).

        Parameters
        ----------
        position: int
            The index which must be removed
        """
        if self._is_new_index:
            raise IndexNotBuildYet

        if position > len(self):
            raise IndexError

        with Index(self.size, volatile=True, trees=self.trees) as tmp_idx:
            shrink = False

            for item, value in self.items_values():
                if item == position:
                    shrink = True
                else:
                    if shrink:
                        item -= 1

                    tmp_idx.tree.add_item(item, value)

            _temp_file = tmp_idx.path

        move(_temp_file, self.path)

        self.refresh()

    def pop(self, position=None):
        """
        Pop-out the index at position, returning it.
        Be advised that this operation is linear on index size ($O(n)$).

        Parameters
        ----------
        position (optional) (default: last position): int
            Removes and returns the value at position.

        Returns
        ----------
        int:
            With the popped item.
        """
        if position:
            value = self[position]
        else:
            inverse_index = -1
            value = self[inverse_index]
            position = len(self) + inverse_index

        self.remove(position)

        return value

    def index(self, tensor):
        """
        Search for the first most similar image compared to the query.

        Parameters
        ----------
        tensor: numpy.ndarray or list
            A vector to search for the most similar.

        Returns
        ----------
        int:
            Describing the most similar resulting index.
        """
        return self.tree.get_nns_by_vector(tensor, n=1)[0]

    def item(self, position, top=10, distances=False):
        """
        Search the index using an internal position

        Parameters
        ----------
        position: int
            The item id within index.

        top (optional, default 10): int
            How many similar items should be returned.

        distances (optional, default 10): bool
            If should be returned also the distances between
            items.

        Returns
        -------
        if distances is True:
            list of tuples:
                Containing pairs of item and distances
        else:
            list:
                Containing similar items.
        """
        return self.tree.get_nns_by_item(
            position,
            top,
            include_distances=distances
        )

    def search(self, tensor, results=16):
        """
        Search for the first most similars image compared to the query.

        Parameters
        ----------
        tensor: numpy.ndarray or list
            A vector to search for the most similar images.

        results: int
            How many results to return. If similar images are less than
            results, it exhausts and will be returned actual total.
        """
        for result in self.tree.get_nns_by_vector(tensor, n=results):
            yield result

    def __len__(self):
        """Return how many items are indexed."""
        return self.tree.get_n_items()

    def __iter__(self):
        """Return an iterable."""
        for value in self.values():
            yield value

    def __next__(self):
        """Iterate over the iterable."""
        self._position += 1

        all_values = list(self.values())

        if self._position < len(all_values):
            return all_values[self._position]

        raise StopIteration

    def group_by(self, top=10, **kwargs):
        """
        Returns all (or some position) on the index that is similar
        with other elements inside index.

        Parameters
        ----------
        top (optional, default 10): int
            How many similar internal images should be returned

        position (optional): int
            Returns the groups based on a specified position.

        Returns
        -------
        list:
            If a position is defined

        or

        dict:
            Generator with a dictionary containing internal ids
            as key and a list of similar images as values.
        """
        position = kwargs.get('position')

        if len(self) <= 1:
            raise EmptyIndexError

        if top >= 1:
            if isinstance(position, int):

                results = self.item(position, top + 1)

                if len(results) > 1:

                    yield results[1:]

            else:

                for item in self.items():

                    yield {
                        item: self.item(
                            item,
                            top + 1
                        )[1:]
                    }
        else:

            raise TopNegativeOrZero

    def export_by_group_by(self, path, top=10, **kwargs):
        """
        Saves images, creating directories, based on their groups.

        Parameters
        ----------
        path: str
            Place to create the directories and export images

        top (optional, default 10):
            How many similar internal images should be returned

        position (optional): int
            Returns the groups based on a specified position.
        """
        for element in FileIO.progress(
            self.group_by(
                top=top,
                position=kwargs.get('position')
            )
        ):
            if isinstance(element, dict):
                item = [*element.keys()][0]
                similars = element[item]
            elif isinstance(element, list):
                item = kwargs['position']
                similars = element

            save_path = os.path.join(
                path,
                str(item)
            )

            os.makedirs(
                save_path,
                exist_ok=True
            )

            try:
                copyfile(
                    self._image_database.mount_file_name(
                        item,
                        'jpg'
                    ),
                    os.path.join(
                        save_path,
                        'group.jpg'
                    )
                )
            except FileNotFoundError:
                continue

            for rank, similar in enumerate(similars):

                original_file_path = self._image_database.mount_file_name(
                    similar,
                    'jpg'
                )

                try:
                    copyfile(
                        original_file_path,
                        os.path.join(
                            save_path,
                            f'{rank + 1}.jpg'
                        )
                    )
                except FileNotFoundError:
                    continue
