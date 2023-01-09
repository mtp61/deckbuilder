#!/usr/bin/env python

import os
import genanki
import argparse

from utils import to_html

def main():
    """
    Converts a single file of a specified format (see anki_file_format.md) into cards
    """

    # parse command line arguments
    parser = argparse.ArgumentParser(
            prog='file2cards',
            description='Converts a single file of a specified format (see anki_file_format.md) into an anki deck')
    parser.add_argument(
            'deck_name',
            type=os.path.abspath,
            help='name of the created deck')
    parser.add_argument(
            'notes_file',
            type=os.path.abspath,
            help='path to the notes file')
    parser.add_argument(
            '--output_dir',
            type=os.path.abspath,
            help='path to the output directory (default: ~/Downloads)',
            default=os.path.expanduser('~/Downloads'))
    parser.add_argument(
            '--image_path',
            type=os.path.abspath,
            help='path to the directory of linked images (default: <notes_file>/attachments')
    args = parser.parse_args()
    if args.image_path is None:
        args.image_path = os.path.join(os.path.split(args.notes_file)[0], 'attachments')

    # create the deck
    #   in practice setting the deck id to the same thing for all decks seems to
    #   work, though i'm not sure if this is best practice
    deck = genanki.Deck(1, args.deck_name)

    # add notes from file
    n_cards = 0
    in_front = False
    in_back = False
    card_front = ''
    card_buffer = []
    media = []
    with open(args.notes_file, 'r') as f:
        lines = f.readlines()
        for i, l in enumerate(lines):
            line = l.strip()
            
            # check to see if we're finishing a card
            if line[:1] == '#' and in_back:
                card_back = commit_buffer(card_buffer)
                card_buffer = []
                media.extend(add_card(deck, card_front, card_back, args.image_path))
                n_cards += 1

                in_back = False
            # ending multi-line front
            elif line[:1] == '#' and in_front:
                if line.lower() != '#### back' and line.lower() != '#### b':
                    print(f'error on line {i}: "{line}"')
                    print('expected #### back')
                    exit(1)

                card_front = commit_buffer(card_buffer)
                card_buffer = []
                in_front = False
                in_back = True

                continue

            # check to see if we're starting a new card
            if line[:3] == '###':
                if in_front:
                    print(f'error on line {i}: "{line}"')
                    print('expected in_front == False')
                    exit(1)

                # look ahead to see if we have a multi-line front
                for l2 in lines[i+1:]:
                    line2 = l2.strip()
                    if line2.lower() == '#### back' or line2.lower() == '#### b':
                        card_buffer.append(line[4:])
                        in_front = True
                        break
                    elif line2[:1] == '#':
                        break

                # if not in a multi-line front, save the front
                if not in_front:
                    card_front = line[4:]
                    in_back = True

                continue

            # add to buffer
            if line[:1] != '#' and (in_front or in_back):
                card_buffer.append(line)
                
    # close card on eof
    if in_back:
        card_back = commit_buffer(card_buffer)
        media.extend(add_card(deck, card_front, card_back, args.image_path))
        n_cards += 1

    # package with media
    package = genanki.Package(deck)
    package.media_files = media

    # write the deck to a file
    output_file = os.path.join(args.output_dir, f'{args.deck_name}.apkg')
    package.write_to_file(output_file)
    print(f'wrote {n_cards} cards to {output_file} from notes file {args.notes_file}')

    # TODO can this be put directly in the anki files?


def commit_buffer(buf: list[str]) -> str:
    out = ''
    for s in buf:
        out += s + '\n'
    return out.strip()


def add_card(deck: genanki.Deck, front: str, back: str, image_path=None):
    media = []
    front_html, front_media = to_html(front, image_path=image_path)
    back_html, back_media = to_html(back, image_path=image_path)
    media.extend(front_media)
    media.extend(back_media)

    deck.add_note(genanki.Note(
            model=genanki.BASIC_MODEL,
            fields=[front_html, back_html]))
    
    return media


if __name__ == '__main__':
    main()
