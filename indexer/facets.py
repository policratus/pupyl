"""
facets Module.

Hyperspace indexing and operations.
"""
import os
from shutil import copy

from annoy import AnnoyIndex

from indexer.exceptions import FileIsNotAnIndex, IndexNotBuildYet
from addendum.operators import intmul
from duplex.file_io import FileIO


class Index:
    """Procedures over multidimensional spaces."""

    def __init__(self, path, size, trees=.001):
        """
        Indexing tensors operations and nearest neighbours search.

        Parameters
        ----------
        path: str
            Location where to load or save the index

        size: int
            Shape of unidimensional vectors which will be indexed

        trees (optional): float
            Defines the number of trees to create based on the dataset
            size. Should be a number between 0 and 1.
        """
        self._position = -1
        self._size = size
        self._path = path
        self._trees = trees

        if os.path.exists(self._path):
            try:
                self._index = AnnoyIndex(size, metric='angular')

                self._index.load(self._path)

                self._is_new_index = False
            except OSError:
                raise FileIsNotAnIndex
        else:
            self._index = AnnoyIndex(size, metric='angular')
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
    def trees(self):
        """Getter for property trees."""
        return self._trees

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

        self.save()

        self._index.unload()

    def save(self):
        """Save the new created index."""
        if self._is_new_index:
            self._index.build(self.size << intmul >> self.trees)

            self._index.save(self.path)

    def items(self):
        """Return the indexed items."""
        for item in range(self._index.get_n_items()):
            if not sum(self._index.get_item_vector(item)) == 0.:
                yield item

    def values(self):
        """Return the indexed values."""
        for item in self.items():
            yield self._index.get_item_vector(item)

    def items_values(self):
        """Return tuples with all items and values."""
        for item, value in zip(self.items(), self.values()):
            yield item, value

    def __getitem__(self, position):
        """Return item at index. Supports negative slicing."""
        if position >= 0:
            return self._index.get_item_vector(position)

        return self._index.get_item_vector(
            self._index.get_n_items() - abs(position)
            )

    def refresh(self):
        """Update all information regarding index file."""
        self._index.unload()
        self._index.load(self.path)

    def append(self, tensor):
        """
        Insert a new tensor at the end of the index.
        Be advised that this operation is linear on index size ($O(n)$).

        Parameters
        ----------
        tensor: numpy.ndarray or list
            A vector to insert into index.
        """
        if self._is_new_index:
            self._index.add_item(len(self), tensor)

        else:
            tmp_file = FileIO.safe_temp_file()

            with Index(tmp_file, self.size, self.trees) as tmp_idx:
                for value in self.values():
                    tmp_idx.append(value)

                tmp_idx.append(tensor)

            copy(tmp_file, self.path)
            os.remove(tmp_file)

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

        tmp_file = FileIO.safe_temp_file()

        with Index(tmp_file, self.size, self.trees) as tmp_idx:
            for item, value in self.items_values():
                if not item == position:
                    tmp_idx.append(value)

        copy(tmp_file, self.path)
        os.remove(tmp_file)

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
        if not position:
            position = len(self) - 1

        value = self[position]

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
        return self._index.get_nns_by_vector(tensor, n=1)[0]

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
        for result in self._index.get_nns_by_vector(tensor, n=results):
            yield result

    def __len__(self):
        """Return how many items are indexed."""
        return self._index.get_n_items()

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
