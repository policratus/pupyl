""" Manage cli arguments"""

import argparse


class PupylCommandLineInterface:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Manage pupyl cli arguments.'
        )
        self.parser.add_argument(
            '--data_dir', help='data directory for image files'
        )
