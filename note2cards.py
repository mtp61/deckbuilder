#!/usr/bin/env python

"""Converts a directory of notes into cards with one note for each card"""

import os
import sys
import genanki
from utils import to_html, OUTPUT_DIR_DEFAULT


# read arguments from command line
if len(sys.argv) != 3 and len(sys.argv) != 4:
    print('usage: note2cards.py deck_name notes_dir [output_dir]')
    exit(1)
deck_name = sys.argv[1]
notes_dir = os.path.expanduser(sys.argv[2])
if len(sys.argv) == 4:
    output_dir = os.path.expanduser(sys.argv[3])
else:
    output_dir = OUTPUT_DIR_DEFAULT

# create the deck
#   in practice setting the deck id to the same thing for all decks seems to
#   work, though I'm not sure if this is best practice
deck = genanki.Deck(1, deck_name)

# add notes from directory
n_cards = 0
for filename in os.listdir(notes_dir):
    if len(filename) < 3 or filename[-3:] != '.md':
        continue

    with open(os.path.join(notes_dir, filename), 'r') as f:
        content = f.read()

        # check for noanki tag
        if '#noanki' in content:
            continue

        out = to_html(content)

        # TODO images--figure out with obsidian first

        deck.add_note(genanki.Note(
                model=genanki.BASIC_MODEL,
                fields=[filename[:-3], out]))
        n_cards += 1

# write the deck to a file
output_file = os.path.join(output_dir, f'{deck_name}.apkg')
genanki.Package(deck).write_to_file(output_file)
print(f'wrote {n_cards} cards to {output_file} from directory {notes_dir}')

# TODO can this be put directly in the anki files?

