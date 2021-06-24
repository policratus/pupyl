"""Operations of file and mime type discovery, based on file content."""

from enum import Enum

from pupyl.duplex import exceptions


class FileHeaderHex(Enum):
    """Describes header hexadecimals for every supported file types.

    The current ones supported are:

    ``JPG, GIF, PNG, TIF, GZP, BZ2, ZIP, LXZ``"""

    JPG = 'ffd8ff'
    GIF = '474946'
    PNG = '89504e'
    TIF = '49492a'
    GZP = '1f8b08'
    BZ2 = '425a68'
    ZIP = '504b03'
    LXZ = 'fd377a'


class FileMimeTypes(Enum):
    """Describes the mime types associated with underlying files.

    The current ones supported are:

    ``JPG, GIF, PNG, TIF, GZP, BZ2, ZIP, LXZ``"""

    JPG = 'image/jpeg'
    GIF = 'image/gif'
    PNG = 'image/png'
    TIF = 'image/tiff'
    GZP = 'application/gzip'
    BZ2 = 'application/x-bzip2'
    ZIP = 'application/zip'
    LXZ = 'application/x-xz'
    TXZ = 'application/tar-xz'
    TGZ = 'application/tar-gz'
    TZ2 = 'application/tar-bz2'


class TarCompressedTypes:
    """Describes all supported tar compressed types.

    The current ones supported are:

    ``GZIP, LZMA, BZIP2``"""
    _types = {
        'gzip': {
            'mimetype': FileMimeTypes.TGZ.value,
            'name': FileMimeTypes.TGZ.name
        },
        'xz': {
            'mimetype': FileMimeTypes.TXZ.value,
            'name': FileMimeTypes.TXZ.name
        },
        'bzip2': {
            'mimetype': FileMimeTypes.TZ2.value,
            'name': FileMimeTypes.TZ2.name
        }
    }

    @classmethod
    def name(cls, sub_type):
        """Returns the name of some sub (file) type.

        Parameters
        ----------
        sub_type: str
            The name of one subtype.

        Returns
        -------
        str:
            With the found subtype.

        Example
        -------
        ``TarCompressedTypes.name('xz') # Returns 'TXZ'``
        """
        return cls._types[sub_type]['name']

    @classmethod
    def mime(cls, sub_type):
        """Return the mime type of some sub type.

        Parameters
        ----------
        sub_type: str
            The name of one subtype.

        Returns
        -------
        str:
            With the found subtype mimetype.

        Example
        -------
        ``TarCompressedTypes.name('xz') # Returns 'application/tar-xz'``
        """
        return cls._types[sub_type]['mimetype']


class FileType:
    """Operations of file type discovery over file content."""

    @staticmethod
    def to_hex(bytess):
        """
        Converts a byte string to its hexadecimal representation.

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
            Bytes of some file.

        Returns
        -------
        str:
            With the header hexadecimal representation.
        """
        return cls.to_hex(bytess[:3])

    @classmethod
    def guess_file_type(cls, bytess, mimetype=False):
        """Heuristically discover the file type for the underlying path.

        Parameters
        ----------
        bytess: bytes
            Bytes of some file.

        mimetype: bool
            If the mimetype should be returned or not.

        Raises
        ------
        FileTypeNotSupportedYet:
            For an unsupported file.

        Returns
        -------
        str:
            With inferred type.
        """
        try:
            header = cls.header(bytess)
        except TypeError as type_error:
            raise exceptions.FileTypeNotSupportedYet from type_error

        for hexa in FileHeaderHex:
            if hexa.value == header:
                if mimetype:

                    return hexa, FileMimeTypes.__members__.get(hexa.name).value

                return hexa.name

        raise exceptions.FileTypeNotSupportedYet

    @staticmethod
    def tar_compressed_types_resolve(sub_type, mimetype=False):
        """Resolves a tar file compression type (if any).

        Parameters
        ----------
        sub_type: str
            The sub type of the tar compressed type.

        mimetype: bool
            If should be returned the MIME type instead of internal
            file type name.

        Returns
        -------
        str:
            With inferred tar (compressed) type
        """
        return TarCompressedTypes.mime(sub_type) \
            if mimetype else TarCompressedTypes.name(sub_type)

    @classmethod
    def is_image(cls, bytess):
        """Return if the read file is an image or not.

        Parameters
        ----------
        bytess: bytes
            Bytes of some file

        Raises
        ------
        FileTypeNotSupportedYet:
            For an unsupported file.

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
