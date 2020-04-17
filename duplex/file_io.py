"""
file_io Module

Operations over files, introspection and more
"""
import os
from urllib.request import urlopen
from enum import Enum, auto
import mimetypes

from duplex import file_types
from duplex.exceptions import FileTypeNotSupportedYet


class Protocols(Enum):
    """
    Defines several possible protocols to be discovered
    """
    UNKNOWN = auto()
    HTTP = auto()
    FILE = auto()


class FileIO(file_types.FileType):
    """
    Operations over files
    """
    @staticmethod
    def _get_url(url):
        """
        Load a file from a remote (http(s)) location

        Parameters
        ----------
        url: str
            The URL where the image are stored

        Returns
        -------
        bytes:
            With image binary information
        """
        return urlopen(url).read()

    @staticmethod
    def _get_local(path):
        """
        Load a local file

        Parameters
        ----------
        path: str
            Local which the file is saved

        Returns
        -------
        bytes:
            With file binary information
        """
        with open(path, 'rb') as ffile:
            return ffile.read()

    @classmethod
    def get(cls, uri):
        """
        Load a file from specified location

        Parameters
        ----------
        uri: str
            Location where the file are stored

        Returns
        -------
        bytes or Enum:
            If successful, returns the image bytes,
            or an Enum describing format was not recognized
        """
        if cls._infer_protocol(uri) is Protocols.FILE:
            return cls._get_local(uri)

        if cls._infer_protocol(uri) is Protocols.HTTP:
            return cls._get_url(uri)

        return Protocols.UNKNOWN

    @staticmethod
    def _infer_protocol(uri):
        """
        Discover the protocol which the passed uri may pertain

        Parameters
        ----------
        uri: str
            URI that describes the image location

        Returns
        -------
        Enum:
            Referencing the discovered protocol
        """
        if uri.startswith('http'):
            return Protocols.HTTP

        if uri.startswith('file') or uri[0] == '/':
            return Protocols.FILE

        return Protocols.UNKNOWN

    def infer_file_type_from_uri(self, uri, mimetype=False):
        """
        Infer the file type from an uri

        Parameters
        ----------
        uri: str
            With file to be analyzed

        mimetype (optional): bool
            If must be returns as mime type or not

        Returns
        -------
        str:
            If described file type
        """
        file_bytes = self.get(uri)

        try:
            if file_bytes is Protocols.UNKNOWN:
                raise FileTypeNotSupportedYet

            return self.guess_file_type(file_bytes, mimetype=mimetype)
        except FileTypeNotSupportedYet:
            file_type = mimetypes.guess_type(uri)[0]

            if file_type:
                return file_type if mimetype else \
                    file_type.split('/')[1].upper()

            raise FileTypeNotSupportedYet

    @staticmethod
    def scan(path):
        """
        Returns a validated file if a path is passed,
        or iterates over a directory

        Parameters
        ----------
        path: str
            A file or directory to scan

        Returns
        -------
        generator of str:
            With the discovery file paths
        """
        if os.path.isfile(path):
            yield os.path.abspath(path)
            
        else:
            for root, _, files in os.walk(path):
                for ffile in files:
                    
                    yield os.path.abspath(f'{root}/{ffile}')
