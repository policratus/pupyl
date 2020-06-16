"""
file_io Module.

Operations over files, introspection and more.
"""
import os
from urllib.request import urlopen, urlparse
from enum import Enum, auto
import mimetypes
import tempfile
import uuid
import csv
import gzip
import zipfile
import bz2
import lzma
from datetime import datetime

from duplex import file_types
from duplex.exceptions import FileTypeNotSupportedYet, FileScanNotPossible


class Protocols(Enum):
    """Defines several possible protocols to be discovered."""

    UNKNOWN = auto()
    HTTP = auto()
    FILE = auto()


class FileIO(file_types.FileType):
    """Operations over files."""

    @staticmethod
    def _get_url(url):
        """
        Load a file from a remote (http(s)) location.

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
        Load a local file.

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
        Load a file from specified location.

        Parameters
        ----------
        uri: str
            Location where the file are stored.

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

    @classmethod
    def get_metadata(cls, uri):
        """
        Return underlying file metadata

        Parameters
        ----------
        uri: str
            Location where the file are stored.

        Returns
        -------
        dict:
            Describing several file metadata
        """
        if cls._infer_protocol(uri) is Protocols.FILE:
            file_statistics = os.stat(uri)

            original_path, original_file_name = os.path.split(uri)
            original_file_size = file_statistics.st_size // 2 ** 10
            original_access_time = cls.timestamp_to_iso8601(
                file_statistics.st_atime
                )

        if cls._infer_protocol(uri) is Protocols.HTTP:
            parsed_url = urlparse(uri)
            file_statistics = urlopen(uri).info()

            original_path, original_file_name = os.path.split(
                f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'
            )
            original_file_size = int(
                file_statistics.get_all('Content-Length')[0]
                ) // 2 ** 10
            original_access_time = file_statistics.get_all('Date')[0]

        return {
            'original_file_name': original_file_name,
            'original_path': original_path,
            'original_file_size': f'{original_file_size}K',
            'original_access_time': original_access_time
        }

    @staticmethod
    def timestamp_to_iso8601(timestamp):
        """
        Convert a Unix epoch integer formatted date to ISO8601 format.
        The converted date is in UTC (GMT-0).

        Parameters
        ----------
        timestamp: int
            With a integer timestamp (seconds after zero hour of 1970)
        """
        return datetime.utcfromtimestamp(timestamp).\
            strftime('%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def _infer_protocol(uri):
        """
        Discover the protocol which the passed uri may pertain.

        Parameters
        ----------
        uri: str
            URI that describes the image location

        Returns
        -------
        Enum:
            Referencing the discovered protocol
        """
        if urlparse(uri).scheme.startswith('http'):
            return Protocols.HTTP

        if uri.startswith('file') or os.path.exists(uri):
            return Protocols.FILE

        return Protocols.UNKNOWN

    def infer_file_type_from_uri(self, uri, mimetype=False):
        """
        Infer the file type from an uri.

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

    @classmethod
    def scan_csv(cls, uri):
        """
        Scanner for CSV formatted text files.

        Parameters
        ----------
        uri: str
            Where csv file resides

        Returns
        -------
        generator of str:
            With the discovery file paths
        """
        csv_string = cls.get(uri)

        if csv_string is Protocols.UNKNOWN:
            raise FileTypeNotSupportedYet

        csv_string = csv_string.decode('utf-8').splitlines()

        reader = csv.reader(csv_string)

        for row in reader:
            yield row

    @classmethod
    def scan_csv_gzip(cls, uri):
        """
        Scanner for CSV formatted text files, compressed with Gzip algorithm.

        Parameters
        ----------
        uri: str
            Where csv file resides

        Returns
        -------
        generator of str:
            With the discovery file paths
        """
        with gzip.open(uri, 'rt') as gzip_file:
            for row in gzip_file:
                yield row.replace('\n', '')

    @staticmethod
    def safe_temp_file(**kwargs):
        """
        Create a secure temporary file name,
        which means a file with an unique name.

        If a file with the same name is found,
        it's deleted a before generating a new unique name.

        Parameters
        ----------
        file_name (optional) (keyword argument): str
            Defining a temporary file to assert.
        """
        temp_dir = tempfile.gettempdir()

        if kwargs.get('file_name'):
            file_name = os.path.join(temp_dir, kwargs.get('file_name'))
        else:
            file_name = os.path.join(temp_dir, str(uuid.uuid4()))

        if os.path.exists(file_name):
            os.remove(file_name)

        return file_name

    @classmethod
    def scan_csv_bzip2(cls, uri):
        """
        Scanner for CSV formatted text files, compressed with Bzip2 algorithm.

        Parameters
        ----------
        uri: str
            Where csv file resides

        Returns
        -------
        generator of str:
            With the discovery file paths
        """
        with bz2.open(uri, 'rt') as bz2_file:
            for row in bz2_file:
                yield row.replace('\n', '')

    @classmethod
    def scan_csv_zip(cls, uri):
        """
        Scanner for CSV formatted text files, compressed with Zip algorithm.

        Parameters
        ----------
        uri: str
            Where csv file resides

        Returns
        -------
        generator of str:
            With the discovery file paths
        """
        for ffile in zipfile.ZipFile(uri).namelist():
            with zipfile.ZipFile(uri).open(ffile) as ufile:
                for row in ufile:
                    yield row.decode('utf-8').replace('\n', '')

    @classmethod
    def scan_csv_xz(cls, uri):
        """
        Scanner for CSV formatted text files, compressed with Lzma algorithm.

        Parameters
        ----------
        uri: str
            Where csv file resides

        Returns
        -------
        generator of str:
            With the discovery file paths
        """
        with lzma.open(uri, 'rt') as xz_file:
            for row in xz_file:
                yield row.replace('\n', '')

    def scan(self, uri):
        """
        Return a validated uri, resolving several cases.

        It also choose the best discovery method.

        Parameters
        ----------
        uri: str
            A file or directory to scan

        Returns
        -------
        generator of str:
            With the discovery file paths
        """
        try:
            inferred_type = self.infer_file_type_from_uri(uri)

            if inferred_type in ('CSV', 'PLAIN'):
                for line in self.scan_csv(uri):
                    yield line

            elif inferred_type == 'GZP':
                for line in self.scan_csv_gzip(uri):
                    yield line

            elif inferred_type == 'ZIP':
                for line in self.scan_csv_zip(uri):
                    yield line

            elif inferred_type == 'BZ2':
                for line in self.scan_csv_bzip2(uri):
                    yield line

            elif inferred_type == 'LXZ':
                for line in self.scan_csv_xz(uri):
                    yield line

            else:
                raise FileScanNotPossible
        except IsADirectoryError:
            for root, _, files in os.walk(uri):
                for ffile in files:
                    yield os.path.abspath(f'{root}/{ffile}')
