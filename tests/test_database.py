"""Unit tests related to storage.database module."""
import tempfile
from os import sep
from shutil import copy
from unittest import TestCase
from os.path import join, relpath, exists

from pupyl.storage.database import ImageDatabase


TEST_TEMP_DIRECTORY = tempfile.gettempdir()
TEST_DIRECTORY = join('tests', 'test_database')
TEST_IMAGE = join('tests', 'test_image.jpg')
TEST_INDEX = 999

TEST_METADATA = {
    'id': 0,
    'original_file_name': 'test_image.jpg',
    'original_path': 'tests',
    'original_file_size': '5K',
    'internal_path': join('tests', 'test_database', '0', '0.jpg')
}

TEST_METADATA_HTTP = {
    'id': 1,
    'original_file_name': 'test_image.jpg',
    'original_path': 'https://domain.com/tests/',
    'original_file_size': '5K'
}


def resolve_original_path(test_metadata):
    """Acknowledge the protocol of original path data."""
    if not test_metadata['original_path'].startswith('http'):
        test_metadata['original_path'] = test_metadata[
            'original_path'].split(sep)[-1]

    return test_metadata


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test___get_item___not_found(self):
        """Unit test for method __get_item__, index not found case."""
        with self.assertRaises(IndexError):
            image_database = ImageDatabase(
                import_images=True,
                data_dir=TEST_DIRECTORY
            )

            _ = image_database[999]

    def test_load_image_metadata_not_found(self):
        """Unit test for method load_image_metadata, index not found case."""
        with self.assertRaises(IndexError):
            image_database = ImageDatabase(
                import_images=True,
                directory=TEST_DIRECTORY
            )

            _ = image_database.load_image_metadata(999)


def test_image_database_definition():
    """Unit test for instance definition for class ImageDatabase."""
    test_import_images = True
    test_bucket_size = 100
    test_image_size = (640, 480)

    image_database = ImageDatabase(
        import_images=test_import_images,
        data_dir=TEST_TEMP_DIRECTORY,
        bucket_size=test_bucket_size,
        image_size=test_image_size
    )

    assert isinstance(image_database, ImageDatabase)
    assert image_database.import_images == test_import_images
    assert image_database._data_dir == TEST_TEMP_DIRECTORY
    assert image_database.bucket_size == test_bucket_size
    assert image_database.image_size == test_image_size


def test___get_item__():
    """Unit test for __get_item__ method."""

    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    test_metadata = image_database[0]
    del test_metadata['original_access_time']

    test_metadata = resolve_original_path(test_metadata)

    assert test_metadata == TEST_METADATA

    test_metadata = image_database[1]
    del test_metadata['original_access_time']

    test_metadata = resolve_original_path(test_metadata)

    assert test_metadata == TEST_METADATA_HTTP


def test___len__():
    """Unit test for __len__ method."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    assert len(image_database) == 1


def test_import_images_property():
    """Unit test for property import_images."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    test_import_images = True
    image_database.import_images = test_import_images
    assert image_database.import_images

    test_import_images = not test_import_images
    image_database.import_images = test_import_images
    assert not image_database.import_images


def test_bucket_size_property():
    """Unit test for property bucket_size."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    test_bucket_size = 999
    image_database.bucket_size = test_bucket_size
    assert image_database.bucket_size == test_bucket_size


def test_image_size_property():
    """Unit test for property image_size."""
    image_database = ImageDatabase(
        data_dir=TEST_DIRECTORY,
        import_images=True
    )

    test_image_size = (320, 200)
    image_database.image_size = test_image_size
    assert image_database.image_size == test_image_size


def test_image_size_property_no_import_images():
    """Unit test for property image_size, no import images case."""
    image_database = ImageDatabase(
        data_dir=TEST_DIRECTORY,
        import_images=False
    )

    test_image_size = (800, 600)
    assert image_database.image_size == test_image_size


def test_insert_import_images():
    """Unit test for method insert, import images case."""
    image_database = ImageDatabase(
        data_dir=TEST_TEMP_DIRECTORY,
        import_images=True
    )

    image_database.insert(10, 'tests/test_image.jpg')

    assert exists(f'{TEST_TEMP_DIRECTORY}/0/10.jpg') \
        and exists(f'{TEST_TEMP_DIRECTORY}/0/10.json')


def test_insert_import_images_gif():
    """Unit test for method insert, import gif images case."""
    image_database = ImageDatabase(
        data_dir=TEST_TEMP_DIRECTORY,
        import_images=True
    )

    image_database.insert(11, 'tests/test_gif.gif')

    assert exists(f'{TEST_TEMP_DIRECTORY}/0/11.gif') \
        and exists(f'{TEST_TEMP_DIRECTORY}/0/11.json')


def test_insert_no_import_images():
    """Unit test for method insert, no import images case."""
    image_database = ImageDatabase(
        data_dir=TEST_TEMP_DIRECTORY,
        import_images=False
    )

    image_database.insert(20, 'tests/test_image.jpg')

    assert not exists(f'{TEST_TEMP_DIRECTORY}/0/20.jpg') and \
        exists(f'{TEST_TEMP_DIRECTORY}/0/20.json')


def test_insert_image_exists_target():
    """Unit test for method insert, image exists on target path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        image_database = ImageDatabase(
            data_dir=temp_dir,
            import_images=True
        )

        test_gif_path = join('tests', 'test_gif.gif')

        copy(test_gif_path, join(temp_dir, '30.gif'))

        image_database.insert(30, test_gif_path)

        assert image_database.load_image_metadata(
            30, filtered=('original_file_name')
        )['original_file_name'] == 'test_gif.gif'


def test_load_image():
    """Unit test for method load_image."""
    test_index = 0

    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    def inst_load_image(index):
        """Closure for method load_image."""
        return image_database.get_image(
            image_database.mount_file_name(index, extension='jpg')
        )

    test_image = image_database.load_image(test_index)

    assert test_image == inst_load_image(test_index)


def test_what_bucket():
    """Unit test for method what_bucket."""
    test_bucket_size = 10 ** 4

    image_database = ImageDatabase(
        import_images=True,
        bucket_size=test_bucket_size
    )

    assert image_database.what_bucket(TEST_INDEX) == \
        TEST_INDEX // test_bucket_size


def test_mount_file_name():
    """Unit test for method mount_file_name."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    expected_path = join(
        TEST_DIRECTORY,
        str(image_database.what_bucket(TEST_INDEX)),
        f'{TEST_INDEX}.json'
    )

    assert image_database.mount_file_name(
        TEST_INDEX, extension='json'
    ) == expected_path


def test_mount_file_name_no_extension():
    """Unit test for method mount_file_name, no extension case."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    expected_path = join(
        TEST_DIRECTORY,
        str(image_database.what_bucket(TEST_INDEX)),
        f'{TEST_INDEX}'
    )

    assert image_database.mount_file_name(TEST_INDEX) == expected_path


def test_load_image_metadata():
    """Unit test for method load_image_metadata."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    test_metadata = image_database.load_image_metadata(0)

    del test_metadata['original_access_time']

    test_metadata = resolve_original_path(test_metadata)

    assert test_metadata == TEST_METADATA

    test_metadata = image_database.load_image_metadata(1)

    del test_metadata['original_access_time']

    test_metadata = resolve_original_path(test_metadata)

    assert test_metadata == TEST_METADATA_HTTP


def test_load_image_metadata_filtered():
    """Unit test for method load_image_metadata, filtered input case."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    test_filter = ('id', 'original_file_size')

    test_metadata = image_database.load_image_metadata(0, filtered=test_filter)

    for key in test_metadata:
        assert key in test_filter


def test_save_image_metadata():
    """Unit test for method save_image_metadata."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    image_database.save_image_metadata(0, TEST_IMAGE)

    test_metadata = image_database.load_image_metadata(0)

    del test_metadata['original_access_time']

    test_metadata['original_path'] = relpath(test_metadata['original_path'])
    test_metadata['internal_path'] = relpath(test_metadata['internal_path'])

    assert test_metadata == TEST_METADATA


def test_load_image_metadata_distances():
    """Unit test for method load_image_metadata, returning distances case."""
    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    test_distance = .9999
    test_metadata = image_database.load_image_metadata(
        0,
        distance=test_distance
    )
    del test_metadata['original_access_time']

    local_test_metadata = TEST_METADATA
    local_test_metadata['distance'] = test_distance

    assert test_metadata == local_test_metadata


def test_list_images():
    """Unit test for method list_images."""
    expected_result = 'tests/test_database/0/0.jpg'

    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    actual_result = [*image_database.list_images()][0]

    assert expected_result == actual_result


def test_list_images_return_ids():
    """Unit test for method list_images, return ids case."""
    expected_path = 'tests/test_database/0/0.jpg'
    expected_index = 0
    expected_result = (expected_index, expected_path)

    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    actual_index_path = [
        *image_database.list_images(
            return_ids=True
        )
    ][0]

    assert actual_index_path == expected_result


def test_list_images_length_filtered():
    """Unit test for method list_images, length filter case."""
    expected_length = 1

    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    actual_result = [*image_database.list_images(top=expected_length)]

    assert len(actual_result) == expected_length


def test_list_images_less_than_count():
    """Unit test for method list_images, less than counter case."""
    expected_length = -1

    image_database = ImageDatabase(
        import_images=True,
        data_dir=TEST_DIRECTORY
    )

    actual_result = [*image_database.list_images(top=expected_length)]

    assert len(actual_result) == 0
