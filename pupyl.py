"""
Manage command line interface
"""

from pupyl.cli import PupylCommandLineInterface
from pupyl.search import PupylImageSearch
from pupyl.web import interface


if __name__ == "__main__":
    cli = PupylCommandLineInterface()
    args = cli.parser.parse_args()
    pupyl = PupylImageSearch()

    pupyl.index(
        args.data_dir
    )

    interface.serve()
