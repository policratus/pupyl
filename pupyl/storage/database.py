"""Operations and storage for images."""

import os
import json

from pupyl.duplex.image import ImageIO


class ImageDatabase(ImageIO):
    """Handling storage and database operations for images."""

    def __init__(self, import_images, data_dir=None, **kwargs):
        """Image storage and operations.

        Parameters
        ----------
        import_images: bool
            If images must be imported (copied) to the internal database or
            not.

        data_dir: str
            Location to save the image storage files and assets. If a value is
            ommited for this parameter, will be created a new temporary folder
            in the underlying (operating system) default temporary directory.

        bucket_size: int
            Defines the number of files per bucket inside the database. Since
            each file and associated assets are saved together, splitting up
            the directories will help avoid issues like ``Too many files``,
            also allowing read parallelization of assets among others features.
            In other words, this parameter describes how many image files will
            be saved on an internal database directory before starting to save
            to another new one.

        image_size: tuple
            Defines the dimensions (in pixels, width x height)
            of saved images on the database. Only has some effect if
            ``import_images`` is True. Case a resize happens, the aspect ratio
            of the original image will be preserved, hence ``image_size`` is an
            approximation. In other words, the image will be resized to
            dimensions close to ``800x600``, but using one pair of dimensions
            that not offends the image aspect.

        Caution
        -------
        If no value is passed to ``data_dir``, all database assets will be
        created on the defined temporary directory. By doing this, be advised
        that all your image search will (probably) vanish after a system
        reboot. If you don't want that this happens, please, define a
        non-volatile ``data_dir``.
        """
        self._import_images = import_images

        if data_dir:
            self._data_dir = os.path.normpath(data_dir)
        else:
            self._data_dir = self.safe_temp_file()

        if kwargs.get('bucket_size'):
            self._bucket_size = kwargs['bucket_size']
        else:
            self._bucket_size = 1000

        if self._import_images:
            if kwargs.get('image_size'):
                self._image_size = kwargs['image_size']
            else:
                self._image_size = (800, 600)

        os.makedirs(self._data_dir, exist_ok=True)

    def __getitem__(self, position):
        """Returns the item at index.

        Parameters
        ----------
        position: int
            The position inside database to return.

        Returns
        -------
        dict:
            With some metadata related to the item.

        Example
        -------
        ``img_db = ImageDatabase(import_images=True, data_dir='pupyl')``

        ``img_db[10]``

        ``# May return:``

        ``{'original_file_name': '2610447919_1b91946bd1.jpg',``
        ``'original_path': '/tmp/tmpekd0cuie',``
        ``'original_file_size': '52K',``
        ``'original_access_time': '2021-06-14T19:07:27',``
        ``'id': 10}``
        """
        return self.load_image_metadata(position)

    def __len__(self):
        """Return how many items are indexed in the database.

        Returns
        -------
        int:
            Describing how may images are indexed on the current database.

        Example
        -------
        ``img_db = ImageDatabase(import_images=True, data_dir='pupyl')``

        ``len(img_db) # May return 709``
        """
        return len([*self.list_images()])

    @property
    def import_images(self):
        """Getter for import_images property.

        Returns
        -------
        bool:
            If images should be imported into the current database or not.
        """
        return self._import_images

    @import_images.setter
    def import_images(self, import_it):
        """Setter for import_images property.

        Parameters
        ----------
        import_it: bool
            If images should be imported into the current database or not.
        """
        self._import_images = import_it

    @property
    def bucket_size(self):
        """Getter for bucket_size property.

        Returns
        -------
        int:
            With how many files per bucket will be stored.
        """
        return self._bucket_size

    @bucket_size.setter
    def bucket_size(self, size):
        """Setter for bucket_size property.

        Parameters
        ----------
        size: int
            Defines how many files per bucket will be saved.
        """
        self._bucket_size = size

    @property
    def image_size(self):
        """Getter for image_size property.

        Returns
        -------
        tuple:
            Describing the internal (approximated) dimensions of each image. If
            ``_import_images`` is undefined, returns by default ``(800x600)``.
        """
        if self._import_images:
            return self._image_size

        return (800, 600)

    @image_size.setter
    def image_size(self, dimensions):
        """Setter for image_size property.

        Parameters
        ----------
        dimensions: tuple
            With dimensions for a image.
        """
        if self._import_images:
            self._image_size = dimensions

    def what_bucket(self, index):
        """Discovers in what bucket the file should be saved.

        Parameters
        ----------
        index: int
            The index that references an image in the database.

        Returns
        -------
        int:
            With the bucket number that the image is saved.
        """
        return index // self._bucket_size

    def mount_file_name(self, index, extension):
        """Creates the full name path that the file will be saved inside
        database.

        Parameters
        ----------
        index: int
            The indexer id associated with the file.

        extension: str
            Describing the file extension.

        Returns
        -------
        str:
            With the full path inside the database.
        """
        return os.path.join(
            self._data_dir,
            str(self.what_bucket(index)),
            f'{index}.{extension}'
        )

    def load_image_metadata(self, index, **kwargs):
        """Loads the metadata for an image inside the database.

        Parameters
        ----------
        index: int
            Regarding the position of some image inside database.

        filtered: iterable
            Describing which fields to filter (or select) for return.

        Returns
        -------
        dict
            Containing the parsed json file.

        Raises
        ------
        IndexError:
            When ``index`` is not found.
        """
        result_file_name = self.mount_file_name(index, 'json')

        try:
            with open(result_file_name) as json_file:
                metadata = json.load(json_file)

                if kwargs.get('filtered'):
                    metadata = {
                        key: value
                        for key, value in metadata.items()
                        if key in kwargs['filtered']
                    }

                return metadata

        except FileNotFoundError:
            raise IndexError from FileNotFoundError

    def save_image_metadata(self, index, uri):
        """Stores image metadata information retrieved from the file.

        Parameters
        ----------
        index: int
            The index related to the image.

        uri: str
            Location where the image is stored.
        """
        bytess = self.get(uri)
        result_file_name = self.mount_file_name(index, 'json')

        os.makedirs(os.path.dirname(result_file_name), exist_ok=True)

        if self.is_image(bytess):
            with open(result_file_name, 'w') as json_file:
                metadata = self.get_metadata(uri)
                metadata['id'] = index

                json.dump(metadata, json_file)

    def insert(self, index, uri):
        """Inserts an image into the database.

        Parameters
        ----------
        index: int
            The index number attributed to the image.

        uri: str
            Where the original file is located.
        """
        if self._import_images:
            self.save_image(
                self.mount_file_name(index, 'jpg'),
                self.compress(
                    self.size(uri, new_size=self._image_size, keep_aspect=True)
                )
            )

        self.save_image_metadata(index, uri)

    def list_images(self, return_index=False, top=None):
        """Returns all images in current database.

        Parameters
        ----------
        return_index: bool
            If the method should also return the file index inside database.

        top: int
            How many pictures from image database should be listed. Not setting
            this parameter (which means not referencing it or setting it
            to zero or below) will return all images in the database.

        Yields
        ------
        tuple or str:
            If ``return_index=True``, a ``tuple`` with ``(int, str)``
            representing respectively the index and the path inside the
            database will be returned. Otherwise, if ``return_index=False``,
            just a ``str`` with the full path will return.
        """
        if top:
            counter = 0

        for root, _, files in os.walk(self._data_dir):

            for ffile in files:

                ffile = os.path.join(root, ffile)

                with open(ffile, 'rb') as t_file:
                    if self.is_image(t_file.read()):

                        if top:
                            counter += 1

                            if counter > top:
                                return

                        if return_index:
                            yield int(
                                os.path.splitext(
                                    os.path.split(ffile)[1]
                                )[0]
                            ), ffile
                        else:
                            yield ffile

    def load_image(self, index):
        """Returns the image data at a specified index.

        Parameters
        ----------
        index: int
            The location of the image inside database.

        Returns
        -------
        bytes:
            Containing image data.
        """
        return self.get_image(self.mount_file_name(index, 'jpg'))
