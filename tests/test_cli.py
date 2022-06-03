"""Unit tests for the command line interface."""
from argparse import Namespace
from unittest import TestCase

from pupyl.cli import PupylCommandLineInterface


CLI = PupylCommandLineInterface()


class TestCases(TestCase):
    """Unit test for special cases."""

    def test_argument_parser_without_parameters(self):
        """Unit test for method argument_parser, without params. case."""

        with self.assertRaises(SystemExit):

            _ = CLI.argument_parser()


def test_parser_index_case():
    """Unit test for the index subcommand with all arguments."""
    sub_command = 'index'
    input_path = 'path/to/images'
    data_dir = 'path/to/assets'

    expected_vars = {
        'data_dir': data_dir,
        'input_images': input_path,
        'options': sub_command,
    }

    args = CLI.argument_parser(
        commands=['--data_dir', data_dir, sub_command, input_path]
    )

    assert vars(args) == expected_vars


def test_parser_serve_case():
    """Unit test for the serve subcommand with all arguments."""
    sub_command = 'serve'
    data_dir = 'path/to/assets'

    expected_vars = {
        'data_dir': data_dir,
        'options': sub_command,
    }

    args = CLI.argument_parser(
        commands=['--data_dir', data_dir, sub_command]
    )

    assert vars(args) == expected_vars


def test_parser_export_case():
    """Unit test for the export subcommand with all arguments."""
    sub_command = 'export'
    query_image = 'path/to/query/image'
    output_dir = 'path/to/output/dir'
    data_dir = 'path/to/assets'
    top = 10

    expected_vars = {
        'data_dir': data_dir,
        'query': query_image,
        'output': output_dir,
        'options': sub_command,
        'top': top,
        'keep_ids': False,
        'keep_names': False
    }

    args = CLI.argument_parser(
        commands=['--data_dir', data_dir, sub_command, query_image, output_dir]
    )

    assert vars(args) == expected_vars

    expected_vars['keep_ids'] = True

    args = CLI.argument_parser(
        commands=[
            '--data_dir', data_dir, sub_command, query_image, output_dir,
            '--keep_ids'
        ]
    )

    assert vars(args) == expected_vars


def test_argument_parser_parameters():
    """Unit test for method argument_parser, passing params. case."""
    sub_command = 'index'
    input_path = 'path/to/images'
    data_dir = 'path/to/assets'

    test_namespace = Namespace(
        data_dir=data_dir,
        input_images=input_path,
        options=sub_command
    )

    test_arguments_parsed = CLI.argument_parser(
        commands=['--data_dir', data_dir, sub_command, input_path]
    )

    assert test_namespace == test_arguments_parsed
