"""
file_types Module.

Operations of file and mime type discovery, based on file content.
"""
from enum import Enum

from pupyl.duplex import exceptions


class FileHeaderHex(Enum):
    """Describes header hexadecimals for every supported file types."""

    JPG = 'ffd8ff'
    GIF = '474946'
    PNG = '89504e'
    TIF = '49492a'
    GZP = '1f8b08'
    BZ2 = '425a68'
    ZIP = '504b03'
    LXZ = 'fd377a'


class FileMimeTypes(Enum):
    """Describes the mime types associated with underlying files."""

    JPG = 'image/jpeg'
    GIF = 'image/gif'
    PNG = 'image/png'
    TIF = 'image/tiff'
    GZP = 'application/gzip'
    BZ2 = 'application/x-bzip2'
    ZIP = 'application/zip'
    LXZ = 'application/x-xz'


class FileType:
    """Operations of file type discovery over file content."""

    @staticmethod
    def to_hex(bytess):
        """
        Convert a byte string to its hexadecimal representation.

        Parameters
        ----------
        bytess: bytes
            Bytes of some file

        Returns
        -------
        str:
            With the hexadecimal representation
        """
        return bytess.hex()

    @classmethod
    def header(cls, bytess):
        """
        Return only the file header or the first three bytes.

        Parameters
        ----------
        bytess: bytes
            Bytes of some file

        Returns
        -------
        str:
            With the header hexadecimal representation
        """
        return cls.to_hex(bytess[:3])

    @classmethod
    def guess_file_type(cls, bytess, mimetype=False):
        """
        Heuristically discover the file type for the underlying path.

        Parameters
        ----------
        bytess: bytes
            Bytes of some file

        mimetype (optional): bool
            If the mimetype should be returned or not

        Returns
        -------
        str:
            With inferred type
        """
        try:
            header = cls.header(bytess)
        except TypeError:
            raise exceptions.FileTypeNotSupportedYet

        for hexa in FileHeaderHex:
            if hexa.value == header:
                if mimetype:

                    return hexa, FileMimeTypes.__members__.get(hexa.name).value

                return hexa.name

        raise exceptions.FileTypeNotSupportedYet

    @classmethod
    def is_image(cls, bytess):
        """
        Return if the read file is an image or not.

        Parameters
        ----------
        bytess: bytes
            Bytes of some file

        Returns
        -------
        bool:
            Describing if the inferred type is image
        """
        try:
            return cls.guess_file_type(
                bytess,
                mimetype=True
            )[1].split('/')[0] == 'image'
        except exceptions.FileTypeNotSupportedYet:
            return False
