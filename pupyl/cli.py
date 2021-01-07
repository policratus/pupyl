""" Manage cli arguments"""

import argparse


class PupylCommandLineInterface:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Manage pupyl cli arguments.'
        )
        self.subparsers = self.parser.add_subparsers(dest='command_name')

        self.index_parser = self.subparsers.add_parser(
            'index', help='index help'
        )
        self.index_parser.add_argument(
            'input_images', help='data directory for image files'
        )
        self.index_parser.add_argument(
            '--data_dir', help='data directory for assets'
        )

        self.serve_parser = self.subparsers.add_parser(
            'serve', help='serve help'
        )
        self.serve_parser.add_argument(
            '--data_dir', help='data directory for assets'
        )
