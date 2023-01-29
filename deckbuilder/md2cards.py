#!/usr/bin/env python

import os
import genanki

from utils import commit_buffer, add_card
from anki_parser import get_args
from mtpreamble_model import get_mtpreamble_model


'''
Converts a single file of a specified markdown format (see anki_file_format.md) into cards
'''
args = get_args()

# create the deck
#   in practice setting the deck id to the same thing for all decks seems to
#   work, though i'm not sure if this is best practice
deck = genanki.Deck(1, args.deck_name)
model = get_mtpreamble_model()

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
            media.extend(add_card(deck, card_front, card_back, args.image_path, model=model))
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
    media.extend(add_card(deck, card_front, card_back, args.image_path, model=model))
    n_cards += 1

# package with media
package = genanki.Package(deck)
package.media_files = media

# write the deck to a file
output_file = os.path.join(args.output_dir, f'{args.deck_name}.apkg')
package.write_to_file(output_file)
print(f'wrote {n_cards} cards to {output_file} from notes file {args.notes_file}')

# TODO can this be put directly in the anki files?
