""" Manage cli arguments"""

import os
import json
import argparse
from pathlib import Path

import termcolor

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
            👥 Contribute to pupyl on https://github.com/policratus/pupyl
            """
        )

        parser.add_argument(
            '--data_dir',
            type=str,
            default=PUPYL_HOME_FOLDER,
            help='data directory for database assets.'
        )

        sub_parsers = parser.add_subparsers(dest='options')

        # Index parser
        index_parser = sub_parsers.add_parser(
            'index', help='indexes images into the database.'
        )
        index_parser.add_argument(
            'input_images',
            help='data directory containing image files to index.'
        )

        sub_parsers.add_parser(
            'serve',
            help='creates a web interface to interact with the database.'
        )

        # Search parser
        search_parser = sub_parsers.add_parser(
            'search', help='search inside a database for similar images.'
        )
        search_parser.add_argument(
            'query', help='URI of an image to use as query.'
        )
        search_parser.add_argument(
            '--top', type=int, default=10, metavar='n',
            help='filters how many results to show.'
        )
        search_parser.add_argument(
            '--metadata', action='store_true',
            help='returns metadata instead of image ids.'
        )

        # Export parser
        export_parser = sub_parsers.add_parser(
            'export',
            help='search inside database, but export result files to a '
            'directory.'
        )
        export_parser.add_argument(
            'query',
            help='URI of an image to use as query.'
        )
        export_parser.add_argument(
            'output', help='directory to export search results as images.'
        )
        export_parser.add_argument(
            '--top', type=int, default=10, metavar='n',
            help='filters how many results to show.'
        )

        export_exclusive_group = export_parser.add_mutually_exclusive_group()
        export_exclusive_group.add_argument(
            '--keep_ids', action='store_true',
            help='should the original image ids must be preserved or not.'
        )
        export_exclusive_group.add_argument(
            '--keep_names', action='store_true',
            help='should the original image names must be preserved or not.'
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

    if args.data_dir == PUPYL_HOME_FOLDER and args.options:
        print(
            termcolor.colored(
                "Since the argument --data_dir wasn't filled,",
                color='cyan'
            ),
            termcolor.colored(
                f'creating pupyl assets on {args.data_dir}', color='cyan'
            )
        )
    elif not args.options:
        cli.parsers().print_help()

    pupyl_search = PupylImageSearch(data_dir=args.data_dir)

    if args.options == 'index':
        pupyl_search.index(
            args.input_images
        )

    elif args.options == 'serve':
        interface.serve(data_dir=args.data_dir)

    elif args.options == 'search':
        for result in pupyl_search.search(
            query=args.query, return_metadata=args.metadata, top=args.top
        ):
            if isinstance(result, dict):
                print(
                    termcolor.colored(
                        json.dumps(result, indent=4), color='green'
                    )
                )
            else:
                print(termcolor.colored(result, color='green'))

    elif args.options == 'export':
        pupyl_search.indexer.export_results(
            args.output, pupyl_search.search(args.query, top=args.top),
            args.keep_ids, args.keep_names
        )
    else:
        cli.parsers().print_help()
