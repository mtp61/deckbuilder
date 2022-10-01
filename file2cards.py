#!/usr/bin/env python

"""Converts a single file of a specified format into cards"""

import os
import sys
import genanki
from utils import to_html, OUTPUT_DIR_DEFAULT


def main():
    # read arguments from the command line
    #   format: file2cards.py deck_name notes_file [output_dir]
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print('usage: file2cards.py deck_name notes_file [output_dir]')
        exit(1)
    deck_name = sys.argv[1]
    notes_file = os.path.expanduser(sys.argv[2])
    if len(sys.argv) == 4:
        output_dir = os.path.expanduser(sys.argv[3])
    else:
        output_dir = OUTPUT_DIR_DEFAULT

    # generate the image path
    image_path = os.path.join(os.path.split(notes_file)[0], 'attachments')

    # TODO should be able to provide this through the command line, only do this as a fallback

    # create the deck
    #   in practice setting the deck id to the same thing for all decks seems to
    #   work, though I'm not sure if this is best practice
    deck = genanki.Deck(1, deck_name)

    # add notes from file
    n_cards = 0
    in_front = False
    in_back = False
    card_front = ''
    card_buffer = []
    media = []
    with open(notes_file, 'r') as f:
        for i, l in enumerate(f.readlines()):
            line = l.strip()
            
            # check to see if we are opening or closing card front or back
            if line[:4] == '####':
                # opening front
                if line.lower() == '#### front':
                    if in_front:
                        print(f'error on line {i}: "{line}"')
                        print('expected in_front == False')
                        exit(1)

                    # commit buffer to back and write card
                    if in_back:
                        card_back = commit_buffer(card_buffer)
                        card_buffer = []
                        media.extend(add_card(deck, card_front, card_back, image_path))
                        n_cards += 1

                    in_front = True
                    in_back = False
                # opening back (and closing front)
                elif line.lower() == '#### back':
                    if not (in_front == True and in_back == False):
                        print(f'error on line {i}: "{line}"')
                        print('expected in_front == True and in_back == False')
                        exit(1)

                    # commit buffer to front
                    card_front = commit_buffer(card_buffer)
                    card_buffer = []

                    in_front = False
                    in_back = True
                # error otherwise
                else:
                    print(f'error on line {i}: "{line}"')
                    exit(1)
            # close card on different heading when in back
            elif line[:1] == '#' and in_back:
                card_back = commit_buffer(card_buffer)
                card_buffer = []
                media.extend(add_card(deck, card_front, card_back, image_path))
                n_cards += 1

                in_back = False
            # append to buffer if in front or back
            elif in_front or in_back:
                card_buffer.append(line)
                
    # close card on eof
    if in_back:
        card_back = commit_buffer(card_buffer)
        media.extend(add_card(deck, card_front, card_back, image_path))
        n_cards += 1

    # package with media
    package = genanki.Package(deck)
    package.media_files = media

    # write the deck to a file
    output_file = os.path.join(output_dir, f'{deck_name}.apkg')
    package.write_to_file(output_file)
    print(f'wrote {n_cards} cards to {output_file} from notes file {notes_file}')

    # TODO can this be put directly in the anki files?


def commit_buffer(buf: list[str]) -> str:
    out = ''
    for s in buf:
        out += s + '\n\n'
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

