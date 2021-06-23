""" Manage cli arguments"""

import os
import argparse
from pathlib import Path

from pupyl.search import PupylImageSearch
from pupyl.web import interface


PUPYL_HOME_FOLDER = os.path.join(Path.home(), 'pupyl')


class PupylCommandLineInterface:
    """Implements the command line interface for pupyl."""

    @staticmethod
    def parsers():
        """Creates parsers and subparsers for pupyl's CLI.

        Returns
        -------
        argparse.ArgumentParser:
            Parsed arguments from command line.
        """

        parser = argparse.ArgumentParser(
            prog='pupyl',
            description="""
            🧿 Manage pupyl CLI arguments. pupyl is a really
            fast image search library which you can index your
            own (millions of) images and find similar images in milliseconds.
            """,
            epilog="""
            👥 Contribute to pupyl on https://github.com/policratus/pupyl'
            """
        )

        sub_parsers = parser.add_subparsers(dest='sub_parser_name')

        index_parser = sub_parsers.add_parser(
            'index', help='indexes images into database'
        )

        index_parser.add_argument(
            'input_images', help='data directory for image files'
        )

        sub_parsers.add_parser(
            'serve', help='creates a web service to interact with database'
        )

        parser.add_argument(
            '--data_dir',
            type=str,
            default=PUPYL_HOME_FOLDER,
            help='data directory for database assets'
        )

        return parser

    @classmethod
    def argument_parser(cls, **kwargs):
        """Renders the command line parsers.

        Parameters
        ----------
        commands: list
            The optional list of parameters to parse.

        Returns
        -------
        argparse.Namespace:
            A namespace with parsed command line arguments whithin.
        """

        commands = kwargs.get('commands')

        if commands:
            return cls.parsers().parse_args(commands)

        return cls.parsers().parse_args()


def pupyl():
    """CLI entry point."""

    cli = PupylCommandLineInterface()
    args = cli.argument_parser()

    if args.data_dir == PUPYL_HOME_FOLDER and args.sub_parser_name:
        print(
            "Since the argument --data_dir wasn't filled, "
            f'creating pupyl assets on {args.data_dir}'
        )

    pupyl_search = PupylImageSearch(data_dir=args.data_dir)

    if args.sub_parser_name == 'index':
        pupyl_search.index(
            args.input_images
        )
    elif args.sub_parser_name == 'serve':
        interface.serve(data_dir=args.data_dir)
    else:
        cli.parsers().print_help()
