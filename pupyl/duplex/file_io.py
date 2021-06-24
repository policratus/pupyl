"""Operations over files, introspection and more."""

import os
import csv
import bz2
import lzma
import gzip
import uuid
import tarfile
import zipfile
import tempfile
import mimetypes
from io import BytesIO
from itertools import cycle
from enum import Enum, auto
from datetime import datetime
import urllib.request as request

import termcolor

from pupyl.duplex.file_types import FileType
from pupyl.duplex.exceptions import FileTypeNotSupportedYet, \
    FileScanNotPossible
from pupyl.addendum.operators import intmul


class Protocols(Enum):
    """Defines several possible protocol enumerators to be discovered.

    Notes
    -----
    The current supported protocols are:

    ``UNKNOWN: Unknown protocol``

    ``HTTP: Hypertext Transfer Protocol (also Secure supported)``

    ``FILE: Local storage file.``
    """

    UNKNOWN = auto()
    HTTP = auto()
    FILE = auto()


class FileIO(FileType):
    """Operations over files.

    Handling operations like temporary directories and files, retrieval of
    remote or local files, progress bars, file metadata, among others.
    """

    @staticmethod
    def pupyl_temp_data_dir():
        """Returns a safe data directory."""
        return os.path.join(
            tempfile.gettempdir(),
            'pupyl'
        )

    @staticmethod
    def _get_url(url):
        """Loads a file from a remote (http(s)) location.

        Parameters
        ----------
        url: str
            The URL where the image are stored.

        Returns
        -------
        bytes:
            With image binary information.
        """
        with request.urlopen(url) as ffile:
            return ffile.read()

    @staticmethod
    def _get_local(path):
        """Loads a local file returning its bytes.

        Parameters
        ----------
        path: str
            Location which the file is saved.

        Returns
        -------
        bytes:
            With file binary information contained on the file.
        """
        with open(path, 'rb') as ffile:
            return ffile.read()

    @classmethod
    def get(cls, uri):
        """Loads a file from specified location, remote or local.

        Parameters
        ----------
        uri: str
            Location where the file are stored.

        Returns
        -------
        bytes or Enum:
            If successful, returns the file bytes,
            or an Enum describing that the format wasn't recognized.
        """
        if cls._infer_protocol(uri) is Protocols.FILE:
            return cls._get_local(uri)

        if cls._infer_protocol(uri) is Protocols.HTTP:
            return cls._get_url(uri)

        return Protocols.UNKNOWN

    @classmethod
    def get_metadata(cls, uri):
        """Returns underlying file metadata.

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
            parsed_url = request.urlparse(uri)

            with request.urlopen(uri) as ffile:
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
                with request.urlopen(uri) as ffile:
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
        """Converts an Unix epoch integer to ISO8601 format.
        The converted date is in UTC (GMT-0).

        Parameters
        ----------
        timestamp: int
            With a integer timestamp (seconds after the zero hour of 1970).

        Returns
        -------
        str:
            A string with formatted date using the mask %Y-%m-%dT%H:%M:%S
        """
        return datetime.utcfromtimestamp(timestamp).\
            strftime('%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def _infer_protocol(uri):
        """Discovers the protocol which the passed uri may pertain.

        Parameters
        ----------
        uri: str
            URI that describes the file location.

        Returns
        -------
        Enum:
            Referencing the discovered protocol
        """
        if request.urlparse(uri).scheme.startswith('http'):
            return Protocols.HTTP

        if uri.startswith('file') or os.path.exists(uri):
            return Protocols.FILE

        return Protocols.UNKNOWN

    def infer_file_type_from_uri(self, uri, mimetype=False):
        """Infers the file type from an uri, with optional mime type discovery.

        Parameters
        ----------
        uri: str
            With the file location to be analyzed.

        mimetype: bool
            If should be returned also the discovered mime type.

        Returns
        -------
        str or tuple:
            str if mimetype is False, this case describing the format
            or tuple if mimetype is True, adding the mimetype to the return.

        Raises
        ------
        FileTypeNotSupportedYet
            For a not supported file type.

        Example
        -------
        ``infer_file_type_from_uri('image.jpg') # Returns 'JPG'``

        ``infer_file_type_from_uri('image.jpg, mimetype=True') # Returns ('JPG'
        , 'image/jpeg')``
        """
        guessed_init_type = mimetypes.guess_type(uri)

        if guessed_init_type[0] == 'application/x-tar':
            return self.tar_compressed_types_resolve(
                guessed_init_type[1],
                mimetype
            )

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
        """Scanner for CSV text files.

        Parameters
        ----------
        uri: str
            Where CSV file resides

        Yields
        ------
        str:
            With the discovery file paths

        Raises
        ------
        FileTypeNotSupportedYet
            For a not supported file type.
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
        """Scanner for CSV formatted text files, compressed with
        gzip algorithm.

        Parameters
        ----------
        uri: str
            Where csv file resides

        Yields
        -------
        str:
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
        """Creates a secure temporary file name, which means a file with an
        unique name.

        If a file with the same name is found, it's deleted before generating
        a new unique name.

        Parameters
        ----------
        file_name: str
            Defining a temporary file to assert.

        Returns
        -------
        str:
            With the complete path of the new temporary file created.
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
        """Scanner for CSV text files, compressed with Bzip2 algorithm.

        Parameters
        ----------
        uri: str
            Where the bzip2 csv file resides.

        Yields
        -------
        str:
            With the discovered file paths.
        """
        file_bytes = cls.get(uri)

        bz2_file = bz2.decompress(
            file_bytes
        ).decode('utf-8').splitlines()

        for row in bz2_file:
            yield row.replace('\n', '')

    @classmethod
    def scan_csv_zip(cls, uri):
        """Scanner for CSV text files, compressed with Zip algorithm.

        Parameters
        ----------
        uri: str
            Where zipped csv file resides.

        Yields
        -------
        str:
            With the discovered file paths.
        """
        file_bytes = BytesIO(cls.get(uri))

        for ffile in zipfile.ZipFile(file_bytes).namelist():
            with zipfile.ZipFile(file_bytes).open(ffile) as ufile:
                for row in ufile:
                    yield row.decode('utf-8').replace('\n', '')

    @classmethod
    def scan_csv_xz(cls, uri):
        """Scanner for CSV text files, compressed with Lzma algorithm.

        Parameters
        ----------
        uri: str
            Where csv xz file resides.

        Yields
        -------
        str:
            With the discovered file paths.
        """
        file_bytes = cls.get(uri)

        xz_file = lzma.decompress(
            file_bytes
        ).decode('utf-8').splitlines()

        for row in xz_file:
            yield row.replace('\n', '')

    def scan(self, uri):
        """Returns a validated uri, resolving several cases related
        to file types and methods for reading it. It also choose the best
        discovery method.

        Parameters
        ----------
        uri: str
            A file or directory to scan.

        Yields
        -------
        str:
            With actual underlying data like bytes internally on the compressed
            file container.
        """
        tar_compressed_file_readers = {
            'TZ2': 'r{stream_type}bz2',
            'TGZ': 'r{stream_type}gz',
            'TXZ': 'r{stream_type}xz'
        }

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

            elif inferred_type in ('TXZ', 'TZ2', 'TGZ'):
                for line in self.scan_compressed_tar_file(
                    uri,
                    tar_compressed_file_readers[inferred_type]
                ):
                    yield line

            else:
                raise FileScanNotPossible
        except (IsADirectoryError, PermissionError):
            for root, _, files in os.walk(uri):
                for ffile in files:
                    yield os.path.join(root, ffile)

    @classmethod
    def scan_compressed_tar_file(cls, uri, file_reader):
        """Scans a compressed tar file.

        Parameters
        ----------
        uri: str
            Location where the tar file is stored.

        file_reader: str
            Suitable file reader type.

        Yields
        ------
        str:
            Paths of the already untarred files on the temporary directory.
        """
        # Waiting to explicitly remove the temporary directory
        temp_directory = tempfile.TemporaryDirectory().name

        inferred_protocol = cls._infer_protocol(uri)

        if inferred_protocol is Protocols.FILE:

            with tarfile.open(
                uri,
                file_reader.format(stream_type=':')
            ) as tar_file:
                tar_file.extractall(temp_directory)

        elif inferred_protocol is Protocols.HTTP:

            with request.urlopen(uri) as opened_url, \
                tarfile.open(
                    fileobj=opened_url,
                    mode=file_reader.format(stream_type='|')
            ) as tar_file:
                for member in cls.progress(tar_file):
                    tar_file.extract(member, path=temp_directory)

        for root, _, files in os.walk(temp_directory):
            for ffile in files:
                yield os.path.join(root, ffile)

    @staticmethod
    def _get_terminal_size():
        """Returns the number of columns of current terminal.

        Returns
        -------
        int:
            Cointaning the number of columns on the current terminal emulator.
        """
        try:
            terminal_half_columns = os.get_terminal_size().columns
        except OSError:
            terminal_half_columns = 128

        return terminal_half_columns

    @classmethod
    def progress(cls, iterable, precise=False, message=None):
        """Utility method to interface process progress bar with users.
        It supports two way of unpacking the iterable, throughout ``precise``
        parameters. If ``precise`` is set to ``False`` (which is the default),
        the parameter ``iterable`` will be unpacked as is. This leads to an
        imprecise rolling of items (in other words, the method doesn't know
        apriori the total number of elements in ``iterable``). Otherwise, if
        ``precise`` is set to ``True``, an ``iterable`` which is not unpacked
        (like a ``generator``) will be first unrolled, which is much slower in
        some cases, but leads to a precise progress bar.

        Parameters
        ----------
        iterable: iter
            Objects which supports iteration.

        precise: bool
            If the progress should be precise
            (with actual percentage of completion) or just an
            interface during process running.

        message: str
            A custom message when reporting progress.

        Yields
        ------
        type:
            It returns any type on the iterable passed through the ``iterable``
            parameter.
        """
        clean_size = 0

        if not message:
            message = 'Processing, please wait:'

        if precise:
            try:
                count = len(iterable)
            except TypeError:
                iterable = [*iterable]
                count = len(iterable)

            print(
                termcolor.colored(
                    message,
                    color='green',
                    attrs=['bold']
                )
            )

            for index, value in enumerate(iterable):

                percentage = (index + 1) / count

                current_terminal_size = cls._get_terminal_size()

                if current_terminal_size >= clean_size:
                    clean_size = current_terminal_size

                columns_to_draw = percentage << intmul >> \
                    current_terminal_size // 4

                bar_to_draw = '🟦' * columns_to_draw
                percent_message = f'{percentage << intmul >> 100}%'

                print(f"\033[A{' ' * clean_size}\033[A")
                print(message, bar_to_draw, percent_message)

                yield value
        else:
            clocks = '🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚'

            for index, value_clock in enumerate(
                    zip(iterable, cycle(clocks))
            ):
                item_message = message + f' {index + 1} items.'

                if cls._get_terminal_size() >= clean_size:
                    clean_size = cls._get_terminal_size()

                print(f"\033[A{' ' * clean_size}\033[A")
                print(value_clock[1], item_message)

                yield value_clock[0]

    @staticmethod
    def resolve_path_end(path):
        """Removes directory separators from the end of
        some path (if it exists).

        Parameters
        ----------
        path: str
            Complete path to be analyzed.

        Returns
        -------
        str:
            A path without an ending character.
        """
        if path[-1] == os.path.sep:
            path = list(path)
            _ = path.pop()

            return ''.join(path)

        return path

    def dump(self, data_dir, output_dir):
        """Reads an entire database tree, compress and export it.

        Parameters
        ----------
        data_dir: str
            The directory containing all database assets.

        output_dir: str
            Location where to save the exported dump file.
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
        """Reads a packaged database and import it.

        Parameters
        ----------
        dump_file: str
            The directory containing all database assets.

        output_dir: str
            Location where to save the export file.
        """
        with tarfile.open(dump_file) as dfile:
            dfile.extractall(output_dir)
