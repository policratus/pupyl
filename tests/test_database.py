"""Unit tests related to storage.database module."""
from os.path import abspath, join, relpath, exists
import tempfile
from unittest import TestCase

from storage.database import ImageDatabase


TEST_TEMP_DIRECTORY = tempfile.gettempdir()
TEST_DIRECTORY = abspath('tests/test_database/')
TEST_IMAGE = abspath('tests/test_image.jpg')
TEST_INDEX = 999

TEST_METADATA = {
    'original_file_name': 'test_image.jpg',
    'original_path': 'tests',
    'original_file_size': '5K'
}


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test___get_item___not_found(self):
        """Unit test for method __get_item__, index not found case."""
        with self.assertRaises(IndexError):
            image_database = ImageDatabase(directory=TEST_DIRECTORY)

            _ = image_database[999]

    def test_load_image_metadata_not_found(self):
        """Unit test for method load_image_metadata, index not found case."""
        with self.assertRaises(IndexError):
            image_database = ImageDatabase(directory=TEST_DIRECTORY)

            _ = image_database.load_image_metadata(999)


def test_image_database_definition():
    """Unit test for instance definition for class ImageDatabase."""
    test_import_images = True
    test_bucket_size = 100
    test_image_size = (640, 480)

    image_database = ImageDatabase(
        import_images=test_import_images,
        directory=TEST_TEMP_DIRECTORY,
        bucket_size=test_bucket_size,
        image_size=test_image_size
    )

    assert isinstance(image_database, ImageDatabase)
    assert image_database.import_images == test_import_images
    assert image_database._directory == TEST_TEMP_DIRECTORY
    assert image_database.bucket_size == test_bucket_size
    assert image_database.image_size == test_image_size


def test___get_item__():
    """Unit test for __get_item__ method."""

    image_database = ImageDatabase(directory=TEST_DIRECTORY)

    test_metadata = image_database[0]
    del test_metadata['original_access_time']

    assert test_metadata == TEST_METADATA


def test_import_images_property():
    """Unit test for property import_images."""
    image_database = ImageDatabase(directory=TEST_DIRECTORY)

    test_import_images = True
    image_database.import_images = test_import_images
    assert image_database.import_images

    test_import_images = not test_import_images
    image_database.import_images = test_import_images
    assert not image_database.import_images


def test_bucket_size_property():
    """Unit test for property bucket_size."""
    image_database = ImageDatabase(directory=TEST_DIRECTORY)

    test_bucket_size = 999
    image_database.bucket_size = test_bucket_size
    assert image_database.bucket_size == test_bucket_size


def test_image_size_property():
    """Unit test for property image_size."""
    image_database = ImageDatabase(
        directory=TEST_DIRECTORY,
        import_images=True
        )

    test_image_size = (320, 200)
    image_database.image_size = test_image_size
    assert image_database.image_size == test_image_size


def test_image_size_property_no_import_images():
    """Unit test for property image_size, no import images case."""
    image_database = ImageDatabase(
        directory=TEST_DIRECTORY,
        import_images=False
        )

    test_image_size = (800, 600)
    assert image_database.image_size == test_image_size


def test_insert_import_images():
    """Unit test for method insert, import images case."""
    image_database = ImageDatabase(
        directory=TEST_TEMP_DIRECTORY,
        import_images=True
        )

    image_database.insert(10, 'tests/test_image.jpg')

    assert exists(f'{TEST_TEMP_DIRECTORY}/0/10.jpg') \
        and exists(f'{TEST_TEMP_DIRECTORY}/0/10.json')


def test_insert_no_import_images():
    """Unit test for method insert, no import images case."""
    image_database = ImageDatabase(
        directory=TEST_TEMP_DIRECTORY,
        import_images=False
        )

    image_database.insert(20, 'tests/test_image.jpg')

    assert not exists(f'{TEST_TEMP_DIRECTORY}/0/20.jpg') and \
        exists(f'{TEST_TEMP_DIRECTORY}/0/20.json')


def test_load_image():
    """Unit test for method load_image."""
    test_index = 0

    image_database = ImageDatabase(directory=TEST_DIRECTORY)

    def inst_load_image(index):
        """Closure for method load_image."""
        return image_database.get_image(
            image_database.mount_file_name(index, 'jpg')
            )

    test_image = image_database.load_image(test_index)

    assert test_image == inst_load_image(test_index)


def test_what_bucket():
    """Unit test for method what_bucket."""
    test_bucket_size = 10 ** 4

    image_database = ImageDatabase(bucket_size=test_bucket_size)

    assert image_database.what_bucket(TEST_INDEX) == \
        TEST_INDEX // test_bucket_size


def test_mount_file_name():
    """Unit test for method what_bucket."""
    image_database = ImageDatabase(directory=TEST_DIRECTORY)
    expected_path = join(
        TEST_DIRECTORY,
        str(image_database.what_bucket(TEST_INDEX)),
        f'{TEST_INDEX}.json'
    )

    assert image_database.mount_file_name(TEST_INDEX, 'json') == expected_path


def test_load_image_metadata():
    """Unit test for method load_image_metadata."""
    image_database = ImageDatabase(directory=TEST_DIRECTORY)

    test_metadata = image_database.load_image_metadata(0)

    del test_metadata['original_access_time']

    test_metadata['original_path'] = relpath(test_metadata['original_path'])

    assert test_metadata == TEST_METADATA


def test_save_image_metadata():
    """Unit test for method save_image_metadata."""
    image_database = ImageDatabase(directory=TEST_TEMP_DIRECTORY)

    image_database.save_image_metadata(0, TEST_IMAGE)

    test_metadata = image_database.load_image_metadata(0)

    del test_metadata['original_access_time']

    test_metadata['original_path'] = relpath(test_metadata['original_path'])

    assert test_metadata == TEST_METADATA
