"""
Manage command line interface
"""

from pupyl.cli import PupylCommandLineInterface
from pupyl.search import PupylImageSearch
from pupyl.web import interface


if __name__ == "__main__":
    CLI = PupylCommandLineInterface()
    ARGS = CLI.parser.parse_args()
    PUPYL = PupylImageSearch(data_dir=ARGS.data_dir)

    if ARGS.command_name == 'index':
        PUPYL.index(
            ARGS.input_images
        )
    elif ARGS.command_name == 'serve':
        interface.serve(data_dir=ARGS.data_dir)
