"""
database module

Operations and storage for images
"""
from enum import Enum, auto
import warnings

import h5py


class FileMode(Enum):
    """
    Defines supported modes within file interaction
    """
    READ_ONLY = auto()
    READ_WRITE = auto()
    CREATE = auto()
    UNKNOWN = auto()


class ImageDatabase:
    """
    Handling of storage and IO operations
    over images
    """
    def __init__(self, path, mode):
        """
        Image storage and operations

        Parameters
        ----------
        path: str
            Location to save the image storage file

        mode: Enum
            Any suitable IO mode described on FileMode enum
        """
        self._path = path
        self._mode = mode

        try:
            self._connection = h5py.File(
                self._path,
                self._resolve_mode(FileMode.CREATE),
                driver=None
            )

            if mode is FileMode.READ_ONLY:
                warnings.warn(
                    f'Opening {self._path} as r/w as it was created right now.'
                )
        except OSError:
            self._connection = h5py.File(
                self._path,
                self._resolve_mode(self._mode),
                driver=None
            )

    @staticmethod
    def _resolve_mode(mode):
        """
        Converts a enum mode to its string format

        Parameters
        ----------
        mode: Enum
            Defines which mode must be converted

        Returns
        -------
        str
        """
        if mode is FileMode.CREATE:
            return 'x'

        if mode is FileMode.READ_ONLY:
            return 'r'

        if mode is FileMode.READ_WRITE:
            return 'r+'

        return FileMode.UNKNOWN

    def __enter__(self):
        """
        Context manager creation
        """
        return self._connection

    def __exit__(self, ptype, value, traceback):
        """
        Context manager destruction
        """
        self._connection.close()

    def get(self, group, name):
        """
        Find and returns a tensor under
        a group and name

        Parameters
        ----------
        group: str
            Name of the group where the tensor are

        name: str
            Description of the name chosen to the tensor

        Returns
        -------
        numpy.ndarray
            The tensor which describes the image
        """
        with ImageDatabase(self._path, FileMode.READ_ONLY) as image_database:
            try:
                return image_database[f'/{group}/{name}'][()]
            except KeyError:
                raise KeyError(f"Key {group}/{name} wasn't found.")

    def add(self, group, name, tensor):
        """
        Adds a new tensor under the group and name specified,
        only if the key doesn't exists

        Parameters
        ----------
        group: str
            Name of the group where the tensor are

        name: str
            Description of the name chosen to the tensor

        tensor: numpy.ndarray
            A tensor representing an image
        """
        with ImageDatabase(self._path, FileMode.READ_WRITE) as image_database:
            groups = image_database.require_group(group)

            groups.create_dataset(
                name,
                shape=tensor.shape,
                data=tensor,
                dtype=tensor.dtype,
                compression='gzip',
                compression_opts=9,
                shuffle=True
            )

            image_database.flush()
