"""Operations and storage for images."""

import os
import json
from shutil import copy, move

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

    def mount_file_name(self, index, **kwargs):
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
        if kwargs.get('extension'):
            extension = kwargs['extension'][1:] \
                if kwargs['extension'][0] == '.' else kwargs['extension']

            return os.path.join(
                self._data_dir,
                str(self.what_bucket(index)),
                f'{index}.{extension}'
            )

        return os.path.join(
            self._data_dir,
            str(self.what_bucket(index)),
            f'{index}'
        )

    def load_image_metadata(self, index, **kwargs):
        """Loads the metadata for an image inside the database.

        Parameters
        ----------
        index: int
            Regarding the position of some image inside database.

        filtered: iterable
            Describing which fields to filter (or select) for return.

        distance: float
            The distance between the tensor represented by ``index``
            and the ``query`` image.

        Returns
        -------
        dict
            Containing the parsed json file.

        Raises
        ------
        IndexError:
            When ``index`` is not found.
        """
        result_file_name = self.mount_file_name(index, extension='json')

        try:
            with open(result_file_name, encoding='utf-8') as json_file:
                metadata = json.load(json_file)

                if kwargs.get('filtered'):
                    metadata = {
                        key: value
                        for key, value in metadata.items()
                        if key in kwargs['filtered']
                    }

                if kwargs.get('distance'):
                    metadata['distance'] = kwargs['distance']

                return metadata

        except FileNotFoundError:
            raise IndexError(
                f'Index not found: {index}'
            ) from FileNotFoundError

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
        result_file_name = self.mount_file_name(index, extension='json')

        os.makedirs(os.path.dirname(result_file_name), exist_ok=True)

        if self.is_image(bytess):
            with open(result_file_name, 'w', encoding='utf-8') as json_file:
                metadata = self.get_metadata(uri)
                metadata['id'] = index
                metadata['internal_path'] = self.mount_file_name(
                    index, extension=self.extension(uri)
                )

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
            mounted_file = self.mount_file_name(
                index, extension=self.extension(uri)
            )

            if not os.path.exists(mounted_file):
                if self.is_animated_gif(uri):
                    image = self.get_image(uri)
                else:
                    image = self.compress(
                        self.size(
                            uri, new_size=self._image_size, keep_aspect=True
                        )
                    )

                self.save_image(mounted_file, image)

        self.save_image_metadata(index, uri)

    def remove(self, index):
        """Removes the image at ``index``.

        Parameters
        ----------
        index: int
            The image index to remove from database.

        Danger
        ------
        Use this method with caution. The deleted image cannot be restored.
        No prompt are shown before deletion.

        Attention
        ---------
        Be advised that this operation is linear on the index size
        (:math:`O(n)`). It provokes changes on the current image ``index``, for
        all indexed images. For instance, if the ``index`` at 54 was deleted,
        every image with index greater than 54 will have the ``id``
        decreased by one.
        """
        for old_id in range(index + 1, len(self)):
            new_id = old_id - 1

            # Renaming images first
            image_old_id = self.load_image_metadata(
                old_id, filtered=['internal_path']
            )['internal_path']

            image_new_id = self.load_image_metadata(
                new_id, filtered=['internal_path']
            )['internal_path']

            move(image_old_id, image_new_id)

            # Now, the metadata files
            metadata_old_id = self.mount_file_name(old_id, extension='json')
            metadata_new_id = self.mount_file_name(new_id, extension='json')

            copy(metadata_old_id, metadata_new_id)

            with open(
                metadata_new_id, 'r+', encoding='utf-8'
            ) as metadata_file:
                metadata = json.load(metadata_file)

                metadata['id'] = new_id
                metadata['internal_path'] = image_new_id

                metadata_file.seek(0)
                json.dump(metadata, metadata_file)

        os.remove(self.mount_file_name(len(self), extension='json'))

    def list_images(self, return_ids=False, top=None):
        """Returns images on current database.

        Parameters
        ----------
        return_ids: bool
            If the method should also return the file ids inside database.

        top: int
            How many pictures from image database should be listed. Not setting
            this parameter (which means not referencing it or setting it
            to zero or below) will return all images in the database.

        Yields
        ------
        tuple or str:
            If ``return_ids=True``, a ``tuple`` with ``(int, str)``
            representing respectively the index and the path inside the
            database will be returned. Otherwise, if ``return_ids=False``,
            just a ``str`` with the full path will return.
        """
        if top:
            counter = 0

        for root, _, files in os.walk(self._data_dir):
            for ffile in files:
                if self.extension(ffile) in ('.jpg', '.gif'):
                    ffile = os.path.join(root, ffile)

                    if top:
                        counter += 1

                        if counter > top:
                            return

                    if return_ids:
                        yield int(
                            os.path.splitext(
                                os.path.split(ffile)[1]
                            )[0]
                        ), ffile
                    else:
                        yield ffile

    def load_image(self, index, as_tensor=False):
        """Returns the image data at a specified index.

        Parameters
        ----------
        index: int
            The location of the image inside database.

        as_tensor: bool
            How to return the image from database: as ``bytes``
            (``as_tensor=False``) or as a ``numpy.ndarray`` tensor
            (``as_tensor=True``)

        Returns
        -------
        bytes or numpy.ndarray:
            Returns image `bytes` (`as_tensor=False`) or
            `numpy.ndarray` (`as_tensor=True`), containing
            image converted to its tensor representation.
        """
        return self.get_image(self.load_image_metadata(
            index, filtered=['internal_path'])['internal_path'], as_tensor
        )
