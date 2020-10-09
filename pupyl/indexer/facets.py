"""
facets Module.

Hyperspace indexing and operations.
"""
import os
from shutil import move

from annoy import AnnoyIndex

from pupyl.indexer.exceptions import FileIsNotAnIndex, \
    IndexNotBuildYet, NoDataDirForPermanentIndex, \
    DataDirDefinedForVolatileIndex, NullTensorError
from pupyl.addendum.operators import intmul
from pupyl.duplex.file_io import FileIO


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
        del exc_type, exc_val, exc_tb

        if self._is_new_index:
            self.tree.build(self.size << intmul >> self.trees)

            self.tree.save(self.path)

        self.tree.unload()

    def items(self):
        """Return the indexed items."""
        for item in range(self.tree.get_n_items()):
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
            self.tree.get_n_items() - abs(position)
        )

    def refresh(self):
        """Update all information regarding index file."""
        self.tree.unload()
        self.tree.load(self.path)

    def append(self, tensor):
        """
        Insert a new tensor at the end of the index.
        Be advised that this operation is linear on index size ($O(n)$).

        Parameters
        ----------
        tensor: numpy.ndarray or list
            A vector to insert into index.
        """
        if sum(tensor) == 0.:
            raise NullTensorError

        if self._is_new_index:
            self.tree.add_item(len(self), tensor)
        else:
            with Index(self.size, volatile=True, trees=self.trees) as tmp_idx:
                for value in self.values():
                    tmp_idx.append(value)

                tmp_idx.append(tensor)

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
            A vector to insert into index.

        Returns
        ----------
        int:
            Describing the most similar resulting index.
        """
        return self.tree.get_nns_by_vector(tensor, n=1)[0]

    def search(self, tensor, results=16):
        """
        Search for the first most similar image compared to the query.

        Parameters
        ----------
        tensor: numpy.ndarray or list
            A vector to insert into index

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
