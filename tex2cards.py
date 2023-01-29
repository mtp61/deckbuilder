#!/usr/bin/env python

import os
import genanki

from utils import commit_buffer, add_card
from anki_parser import get_args
from mtpreamble_model import get_mtpreamble_model


LINE_BEGIN = '\\begin{card}'
LINE_MID = '\\medskip'
LINE_END = '\\end{card}'


'''
Converts a single file of a specified latex format (see anki_file_format.tex) into cards
'''
args = get_args()

model = get_mtpreamble_model()
deck = genanki.Deck(1, args.deck_name)

# add notes from file
with open(args.notes_file, 'r') as f:
    lines = f.readlines()

n_cards = 0
card_buffer = []
in_front, in_back = False, False
card_front = None
for i, line in enumerate(lines):
    line = line.strip()

    # opening the front
    if LINE_BEGIN in line:
        if in_front:
            print(f'ERROR [{i}]: Opening the front of a card but got `in_front = True`')
            exit(1)
        if in_back:
            print(f'ERROR [{i}]: Opening the front of a card but got `in_back = True`')
            exit(1)

        in_front = True
    # opening the back
    elif LINE_MID in line:
        if not in_front:
            print(f'ERROR [{i}]: Opening the back of a card but got `in_front = False`')
            exit(1)
        if in_back:
            print(f'ERROR [{i}]: Opening the back of a card but got `in_back = True`')
            exit(1)

        card_front = commit_buffer(card_buffer)
        in_front = False
        in_back = True
    # closing the back
    elif LINE_END in line:
        if in_front:
            print(f'ERROR [{i}]: Closing the back of a card but got `in_front = True`')
            exit(1)
        if not in_back:
            print(f'ERROR [{i}]: Closing the back of a card but got `in_back = False`')
            exit(1)

        add_card(deck, card_front, commit_buffer(card_buffer), model=model)
        card_buffer = []
        n_cards += 1
        in_back = False
    elif in_front or in_back:
        card_buffer.append(line)

# write the deck to a file
package = genanki.Package(deck)
deck_name = args.deck_name if '.apkg' in args.deck_name else args.deck_name + '.apkg'
output_file = os.path.join(args.output_dir, deck_name)
package.write_to_file(output_file)
print(f'wrote {n_cards} cards to {output_file} from notes file {args.notes_file}')
