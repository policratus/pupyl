"""Operations for volatile resources."""

import os
import uuid
import tempfile
from pathlib import Path
from platform import system


class SafeTemporaryResource:
    """Creates temporary files or directories."""

    def __init__(self, **kwargs):
        """Defines the temporary resource.

        Parameters
        ----------
        file_name: str
            To define a name for the temporary file. If the file
            exists, it will try to delete the file before anything else.

        directory_name: str
            To define a name for the temporary directory. If the directory
            not exists, it will be created.

        user_defined: bool
            If should be created a temporary resource based on user's names
            or not.
        """
        self._file_name = kwargs.get('file_name')
        self._directory_name = kwargs.get('directory_name')

        if system() == 'Windows':
            default_temp_dir = str(Path.home())
        else:
            default_temp_dir = tempfile.gettempdir()

        if kwargs.get('user_defined'):
            if self._directory_name and not self._file_name:
                self._temp_path = os.path.join(
                    default_temp_dir, self._directory_name
                )

                os.mkdirs(self._temp_path, exists_ok=True)
            elif not self._directory_name and self._file_name:
                self._temp_path = os.path.join(
                    default_temp_dir, self._file_name
                )
        else:
            if system() == 'Windows':
                self._temp_path = os.path.join(
                    default_temp_dir, str(uuid.uuid4())
                )

                os.mkdir(self._temp_path)
            else:
                self._temp_dir = tempfile.TemporaryDirectory()
                self._temp_path = self._temp_dir.name

    @property
    def name(self):
        """Getter for property name."""
        return self._temp_path

    def __str__(self):
        """Returns the string representation."""
        return self.name

    def __enter__(self):
        """Opens the SafeTemporaryResource context."""
        return self

    def cleanup(self):
        """Clean up temporary resources."""
        try:
            self._temp_dir.cleanup()
        except AttributeError:
            os.system(f'rmdir /s /q "{self.name}"')

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Opens the SafeTemporaryResource context."""
        del exc_type, exc_val, exc_tb
        
        self.cleanup()
