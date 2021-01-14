""" Manage cli arguments"""

import argparse

from pupyl.search import PupylImageSearch
from pupyl.web import interface


class PupylCommandLineInterface:
    """Implements the CLI for pupyl"""

    @staticmethod
    def parsers():
        """Create parsers and subparsers for CLI"""

        parser = argparse.ArgumentParser(
            prog='pupyl',
            description="""
            🧿 Manage pupyl CLI arguments. pupyl is a really
            fast image search library which you can index your
            own (millions of) images and find similar images in milliseconds.
            """,
            epilog='👥 Contribute to pupyl on https://github.com/policratus/pupyl'
        )

        parser.add_argument(
            'data_dir', help='data directory for database assets'
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

        return parser

    @classmethod
    def argument_parser(cls, **kwargs):
        """
        Render the parsers.

        Parameters
        ----------
        **commands (optional): list
            The optional list of parameters to parse.
        """

        commands = kwargs.get('commands')

        if commands:
            return cls.parsers().parse_args(commands)

        return cls.parsers().parse_args()


if __name__ == '__main__':
    CLI = PupylCommandLineInterface()
    ARGS = CLI.argument_parser()

    PUPYL = PupylImageSearch(data_dir=ARGS.data_dir)

    if ARGS.sub_parser_name == 'index':
        PUPYL.index(
            ARGS.input_images
        )
    elif ARGS.sub_parser_name == 'serve':
        interface.serve(data_dir=ARGS.data_dir)
    else:
        CLI.parsers().print_help()
