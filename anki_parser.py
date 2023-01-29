import argparse
import os


def get_args():
    '''
    Return an 'args' object with parameters:
        deck_name
        notes_file
        output_dir
        image_path
    '''
    parser = argparse.ArgumentParser(
            prog='file2cards',
            description='Converts a single file of a specified format (see anki_file_format.md) into an anki deck')
    parser.add_argument(
            '-d', '--deck_name',
            type=str,
            required=True,
            help='name of the created deck')
    parser.add_argument(
            '-n', '--notes_file',
            type=os.path.abspath,
            required=True,
            help='path to the notes file')
    parser.add_argument(
            '-o', '--output_dir',
            type=os.path.abspath,
            default=os.path.expanduser('~/Downloads'),
            help='path to the output directory (default: ~/Downloads)')
    parser.add_argument(
            '-i', '--image_path',
            type=os.path.abspath,
            help='path to the directory of linked images (default: <notes_file>/attachments')
    args = parser.parse_args()
    if args.image_path is None:
        args.image_path = os.path.join(os.path.split(args.notes_file)[0], 'attachments')

    return args
