"""
database module.

Operations and storage for images.
"""
import os
import json

from pupyl.duplex.image import ImageIO


class ImageDatabase(ImageIO):
    """Handling of storage and IO operations over images."""

    def __init__(self, import_images, data_dir=None, **kwargs):
        """
        Image storage and operations.

        Parameters
        ----------
        import_images: bool
            If the images must be copied to internal database or not.

        data_dir (optional) (default=self.safe_temp_file()): str
            Location to save the image storage files

        **bucket_size (optional) (default=1000): int
            Define the size of file buckets. In other words, how much
            files to save on a directory.

        **image_size (optional) (default=(800, 600)): tuple
            Define the dimensions of saved image. Only has some effect
            if import_images is True.
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
        """Return the item at index."""
        return self.load_image_metadata(position)

    def __len__(self):
        """Return how many items are indexed."""
        return len([*self.list_images()])

    @property
    def import_images(self):
        """Getter for import_images property."""
        return self._import_images

    @import_images.setter
    def import_images(self, import_it):
        """Setter for import_images property."""
        self._import_images = import_it

    @property
    def bucket_size(self):
        """Getter for bucket_size property."""
        return self._bucket_size

    @bucket_size.setter
    def bucket_size(self, size):
        """Setter for bucket_size property."""
        self._bucket_size = size

    @property
    def image_size(self):
        """Getter for image_size property."""
        if self._import_images:
            return self._image_size

        return (800, 600)

    @image_size.setter
    def image_size(self, dimensions):
        if self._import_images:
            self._image_size = dimensions

    def what_bucket(self, index):
        """
        Discover in what bucket the file should be saved.

        Parameters
        ----------
        index: int
            The index number which file will be referenced.

        Returns
        -------
        int:
            With the chosen bucket
        """
        return index // self._bucket_size

    def mount_file_name(self, index, extension):
        """
        Create the name of the posterior saved file.

        Parameters
        ----------
        index: int
            The indexer id associated with the file

        extension: str
            Describing the file extension
        """
        return os.path.join(
            self._data_dir,
            str(self.what_bucket(index)),
            f'{index}.{extension}'
        )

    def load_image_metadata(self, index, **kwargs):
        """
        Return the metadata inside image file metadata.

        Parameters
        ----------
        index: int
            Related to metadata file stored.

        **filtered (optional): iterable
            Describing which fields to filter (or select) for return.

        Returns
        -------
        dict
            Containing the parsed json file.
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
            raise IndexError

    def save_image_metadata(self, index, uri):
        """
        Store image metadata.

        Parameters
        ----------
        index: int
            The index related to the image.

        uri: str
            Local where image is stored.
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
        """
        Insert an image to database.

        Parameters
        ----------
        index: int
            The index number attributed to the image.

        uri: str
            Where the original file are located
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
        """
        Return all images in current database.

        Parameters
        ----------
        return_index (optional)(default: False): bool
            If the method should also return the file index inside database.

        top (optional): int
            How many pictures from image database should be listed. Not setting
            this parameter (which means not referencing it or setting it
            to zero or below) will return all images in the database.
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
        """Return the image data at specified index."""
        return self.get_image(self.mount_file_name(index, 'jpg'))
