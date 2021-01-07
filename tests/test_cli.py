"""Unit tests for the command line interface."""

from pupyl.cli import PupylCommandLineInterface

CLI = PupylCommandLineInterface()


def test_index_parser_with_all_arguments():
    """Unit test for the index subcommand with all arguments."""
    SUBCOMMAND = 'index'
    INPUT_PATH = 'path/to/images'
    DATA_DIR = 'path/to/assets'
    EXPECTED_VARS = {
        'command_name': SUBCOMMAND,
        'input_images': INPUT_PATH,
        'data_dir': DATA_DIR
    }

    args = CLI.parser.parse_args(
        [SUBCOMMAND, INPUT_PATH, '--data_dir', DATA_DIR]
    )

    assert vars(args) == EXPECTED_VARS


def test_index_parser_with_mandatory_arguments_only():
    """Unit test for the index subcommand with only mandatory arguments."""
    SUBCOMMAND = 'index'
    INPUT_PATH = 'path/to/images'
    EXPECTED_VARS = {
        'command_name': SUBCOMMAND,
        'input_images': INPUT_PATH,
        'data_dir': None
    }

    args = CLI.parser.parse_args([SUBCOMMAND, INPUT_PATH])

    assert vars(args) == EXPECTED_VARS


def test_serve_parser_with_no_arguments():
    """Unit test for the serve subcommand with no arguments."""
    SUBCOMMAND = 'serve'
    EXPECTED_VARS = {
        'command_name': SUBCOMMAND,
        'data_dir': None
    }

    args = CLI.parser.parse_args([SUBCOMMAND])

    assert vars(args) == EXPECTED_VARS


def test_serve_parser_with_optional_argument():
    """Unit test for the serve subcommand with optional argument."""
    SUBCOMMAND = 'serve'
    DATA_DIR = 'path/to/assets'
    EXPECTED_VARS = {
        'command_name': SUBCOMMAND,
        'data_dir': DATA_DIR
    }

    args = CLI.parser.parse_args([SUBCOMMAND, '--data_dir', DATA_DIR])

    assert vars(args) == EXPECTED_VARS
