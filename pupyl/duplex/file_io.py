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
import tarfile
from datetime import datetime
from itertools import cycle
from io import BytesIO

import termcolor

from pupyl.duplex.file_types import FileType
from pupyl.duplex.exceptions import FileTypeNotSupportedYet, \
    FileScanNotPossible
from pupyl.addendum.operators import intmul


class Protocols(Enum):
    """Defines several possible protocols to be discovered."""

    UNKNOWN = auto()
    HTTP = auto()
    FILE = auto()


class FileIO(FileType):
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
        with urlopen(url) as ffile:
            return ffile.read()

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

            with urlopen(uri) as ffile:
                file_statistics = ffile.info()

            original_path, original_file_name = os.path.split(
                f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'
            )

            try:
                measured_size = int(
                    file_statistics.get_all(
                        'Content-Length'
                    )[0]
                )
            except TypeError:
                with urlopen(uri) as ffile:
                    measured_size = len(ffile.read())

            original_file_size = measured_size // (2 ** 10)

            try:
                original_access_time = file_statistics.get_all('Date')[0]
            except TypeError:
                original_access_time = datetime.strftime(datetime.now(), '%c')

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
        except FileTypeNotSupportedYet as file_type_not_supported_yet:
            file_type = mimetypes.guess_type(uri)[0]

            if file_type:
                return file_type if mimetype else \
                    file_type.split('/')[1].upper()

            raise file_type_not_supported_yet

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
            yield row[0]

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
        file_bytes = cls.get(uri)

        gzip_file = gzip.decompress(
            file_bytes
        ).decode('utf-8').splitlines()

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

    @staticmethod
    def pupyl_temp_data_dir():
        """Returns a safe data directory."""
        return os.path.join(
            tempfile.gettempdir(),
            'pupyl'
        )

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
        file_bytes = cls.get(uri)

        bz2_file = bz2.decompress(
            file_bytes
        ).decode('utf-8').splitlines()

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
        file_bytes = BytesIO(cls.get(uri))

        for ffile in zipfile.ZipFile(file_bytes).namelist():
            with zipfile.ZipFile(file_bytes).open(ffile) as ufile:
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
        file_bytes = cls.get(uri)

        xz_file = lzma.decompress(
            file_bytes
        ).decode('utf-8').splitlines()

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
                    yield os.path.join(root, ffile)

    @staticmethod
    def progress(iterable, precise=False):
        """
        Utility method to interface process progress bar with users.
        It supports two way of unpacking the iterable, throughout `precise`
        parameters. If `precise` is set to `False` (which is the default),
        the parameter `iterable` will be unpacked as is. This leads to an
        imprecise rolling of items (in other words, the method doesn't know
        apriori the total number of elements in `iterable`). Otherwise, if
        `precise` is set to `True`, an `iterable` which is not unpacked (like
        and `generator`) will be first unrolled, which is much slower in some
        cases, but leads to a precise progress bar.

        Parameters
        ----------
        iterable: iter
            Objects which supports iteration.

        precise (optional)(default: False): bool
            If the progress should be precise
            (with actual percentage of completion) or just an
            interface during process running.
        """
        if precise:
            try:
                count = len(iterable)
            except TypeError:
                iterable = [*iterable]
                count = len(iterable)

            print(
                termcolor.colored(
                    'Processing, please wait.',
                    color='green',
                    attrs=['bold']
                )
            )

            for index, value in enumerate(iterable):
                try:
                    terminal_half_columns = os.get_terminal_size().columns // 4
                except OSError:
                    terminal_half_columns = 64

                percentage = (index + 1) / count

                columns_to_draw = percentage << intmul >> terminal_half_columns

                print(
                    ' ' + ('🟦' * columns_to_draw),
                    f'{percentage << intmul >> 100}%',
                    end='\r'
                )

                yield value
        else:
            clocks = '🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚'

            for index, value_clock in enumerate(
                    zip(iterable, cycle(clocks))
            ):
                print(
                    ' ' + value_clock[1],
                    f' Processed {index + 1} items.',
                    end='\r'
                )

                yield value_clock[0]

    @staticmethod
    def resolve_path_end(path):
        """
        Removes directory separators from the end of
        some path (if exists).

        Parameters
        ----------
        path: str
            Complete path to be analyzed.
        """
        if path[-1] == os.path.sep:
            path = list(path)
            _ = path.pop()

            return ''.join(path)

        return path

    def dump(self, data_dir, output_dir):
        """
        Read an entire database tree, compress and export it.

        Parameters
        ----------
        data_dir: str
            The directory containing all database assets.

        output_dir: str
            Location where to save the export file.
        """
        data_dir = self.resolve_path_end(data_dir)
        base_name = os.path.basename(data_dir)
        dump_name = '.'.join((base_name, 'pupyl'))
        dump_path = os.path.join(output_dir, dump_name)

        with tarfile.open(dump_path, 'w:xz') as tar:
            for path in self.progress(self.scan(data_dir)):
                path_split = path.split(os.path.sep)
                archive_name = os.path.join(
                    *path_split[path_split.index(base_name):]
                )

                tar.add(path, arcname=archive_name)

    @staticmethod
    def bind(dump_file, output_dir):
        """
        Read a packaged database and import it.

        Parameters
        ----------
        dump_file: str
            The directory containing all database assets.

        output_dir: str
            Location where to save the export file.
        """
        with tarfile.open(dump_file) as dfile:
            dfile.extractall(output_dir)
