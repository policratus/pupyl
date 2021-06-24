"""Hyperspace indexing and operations."""

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
        """Indexing tensors operations and approximate nearest neighbours
        search.

        Parameters
        ----------
        size: int
            Shape of unidimensional vectors which will be indexed

        data_dir: str
            Location where to load or save the index

        trees: float
            Defines the factor over the number of trees to be created based on
            the dataset size. Should be a number between 0 and 1.

        volatile: bool
            If the index will be temporary or not.

        Raises
        ------
        OSError:
            When the ``data_dir`` parameter is not a directory.
        NoDataDirForPermanentIndex:
            When no ``data_dir`` was passed for a permament index.
        DataDirDefinedForVolatileIndex:
            If a ``data_dir`` was defined for a volatile index.
        FileIsNotAnIndex:
            When an index was tried to be loaded but it wasn't a valid file.
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
        """Getter for property size.

        Returns
        -------
        int:
            Describing the size of a ANN tree.
        """
        return self._size

    @property
    def path(self):
        """Getter for property path.

        Returns
        -------
        str:
            With the path set.
        """
        return self._path

    @property
    def index_name(self):
        """Getter for property index_name.

        Returns
        -------
        str:
            With current index name.
        """
        return 'pupyl.index'

    @property
    def volatile(self):
        """Getter for property volatile.

        Returns
        -------
        bool:
            If the index is volatile or not.
        """
        return self._volatile

    @property
    def trees(self):
        """Getter for property trees.

        Returns
        -------
        float:
            With the factor over the index size to make trees.
        """
        return self._trees

    @trees.setter
    def trees(self, trees):
        """Setter for property trees.

        Parameters
        ----------
        trees: float
            The factor over index size to make trees.
        """
        self._trees = trees

    def __enter__(self):
        """Context opening for an index.

        Returns
        -------
        self:
            Context initialization.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context closing for an index."""
        if not exc_type:

            del exc_type, exc_val, exc_tb

            if self._is_new_index:
                self.tree.build(self.size << intmul >> self.trees)

                self.tree.save(self.path)

            self.tree.unload()

    def items(self):
        """Returns indexed items.

        Yields
        ------
        int:
            With item identification.
        """
        for item in range(len(self)):
            yield item

    def values(self):
        """Returns indexed values.

        Yields
        ------
        list:
            With indexed tensors.
        """
        for item in self.items():
            yield self.tree.get_item_vector(item)

    def items_values(self):
        """Returns all items and values.

        Yields
        ------
        tuple:
            With an ``int`` representing its id and a ``list`` with the actual
            tensor.
        """
        for item, value in zip(self.items(), self.values()):
            yield item, value

    def __getitem__(self, position):
        """Return item at index, supporting negative slicing.

        Parameters
        ----------
        position: int
            The id of desired item to be returned.

        Returns
        -------
        list:
            With indexed tensors.

        Example
        -------
        ``index[10] # Returns the 10th item.``

        ``index[-1] # Returns the last item.``
        """
        if position >= 0:
            return self.tree.get_item_vector(position)

        return self.tree.get_item_vector(
            len(self) - abs(position)
        )

    def refresh(self):
        """Updates all information regarding the index file, first unloading
        it, followed by reloading back the index.
        """
        self.tree.unload()
        self.tree.load(self.path)

    def append(self, tensor, check_unique=False):
        """
        Inserts a new tensor at the end of the index.

        Attention
        ---------
        Be advised that this operation is linear on the index size
        (:math:`O(n)`).

        Parameters
        ----------
        tensor: numpy.ndarray or list
            The tensor to insert into the index.

        check_unique: bool
            Defines if the append method should verify the existence
            of a really similar tensor on the current index. In other words,
            it checks for the unicity of the value.

        Warning
        -------
        Be advised that the unicity check (``check_unique=True``) creates an
        overhead on the append process.

        Raises
        ------
        NullTensorError:
            If a null (empty) tensor is passed through.
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
                        'are on. Refusing to store this tensor again.'
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
        """Removes the tensor at ``position`` from the database.

        Attention
        ---------
        Be advised that this operation is linear on the index size
        (:math:`O(n)`).

        Parameters
        ----------
        position: int
            The index that must be removed.

        Raises
        ------
        IndexNotBuildYet:
            If was tried to remove a tensor from a not built yet index file.
        IndexError:
            If ``position`` is bigger than the index current size.
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
        """Pops-out the index at position, returning it.

        Attention
        ---------
        Be advised that this operation is linear on the index size
        (:math:`O(n)`).

        Parameters
        ----------
        position: int
            Removes and returns the value at ``position``.

        Returns
        ----------
        int:
            With the popped-out item.
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
        """Searchs for the first and most similar image compared to the query
        image.

        Parameters
        ----------
        tensor: numpy.ndarray or list
            A vector to search for the most similar.

        Returns
        -------
        int:
            Describing the most similar resulting index.
        """
        return self.tree.get_nns_by_vector(tensor, n=1)[0]

    def item(self, position, top=10, distances=False):
        """Searchs the index using an internal position

        Parameters
        ----------
        position: int
            The item id within index.

        top: int
            How many similar items should be returned.

        distances: bool
            If should be returned also the distances between items.

        Returns
        -------
        list of tuples:
            if distances is ``True``, this ``list`` containing pairs of items
            and distances.
        list:
            if distances is ``False``, this ``list`` containing similar items.
        """
        return self.tree.get_nns_by_item(
            position,
            top,
            include_distances=distances
        )

    def search(self, tensor, results=16):
        """Searchs for the most similar images compared to the query image (or
        with increasing distances).

        Parameters
        ----------
        tensor: numpy.ndarray or list
            A vector to search for the most similar ones.

        results: int
            How many results to return. If similar images are less than
            ``results``, it exhausts and will be returned current total
            results.

        Yields
        ------
        int:
            Representing the index of the most similar, the second one and so
            on.
        """
        for result in self.tree.get_nns_by_vector(tensor, n=results):
            yield result

    def __len__(self):
        """Returns how many items are indexed.

        Returns
        -------
        int:
            Describing how many items are indexed.

        Example
        -------
        ``len(index) # Will return 10 for an index with 10 elements indexed``
        """
        return self.tree.get_n_items()

    def __iter__(self):
        """Returns an iterable for the index.

        Yields
        ------
        list:
            With indexed tensors.
        """
        for value in self.values():
            yield value

    def __next__(self):
        """Iterates over the iterable.

        Returns
        -------
        list:
            With an indexed tensor.

        Raises
        ------
        StopIteration:
            When the iterable is exhausted.
        """
        self._position += 1

        all_values = list(self.values())

        if self._position < len(all_values):
            return all_values[self._position]

        raise StopIteration

    def group_by(self, top=10, **kwargs):
        """Returns all (or some position) on the index which is similar
        with each other inside index.

        Parameters
        ----------
        top: int
            How many similar internal images should be returned.

        position: int
            Returns the groups based on a specified position.

        Yields
        ------
        list:
            If ``position`` is defined.
        dict:
            Generator with a dictionary containing internal ids
            as key and a list of similar images as values.

        Raises
        ------
        EmptyIndexError:
            If the underlying index is null.
        TopNegativeOrZero:
            If ``top`` parameter is zero or below.
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
        """Export images, creating directories based on their groups.

        Parameters
        ----------
        path: str
            Place to create the directories and export the images.

        top: int
            How many similar internal images should be filtered.

        position: int
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
