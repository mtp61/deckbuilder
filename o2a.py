#!/usr/bin/env python

import genanki
import os
import markdown
import sys


OUTPUT_DIR_DEFAULT = os.path.expanduser('~/Downloads')

# read arguments from command line
if len(sys.argv) != 3 and len(sys.argv) != 4:
    print('usage: o2a.py deck_name notes_dir [output_dir]')
    exit(1)
deck_name = sys.argv[1]
notes_dir = os.path.expanduser(sys.argv[2])
if len(sys.argv) == 4:
    output_dir = os.path.expanduser(sys.argv[3])
else:
    output_dir = OUTPUT_DIR_DEFAULT

# create the deck
# in practice setting the deck id to the same thing for all decks seems to
# work, though I'm not sure if this is best practice
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

        # remove obsidian links 
        content = content.replace('[[', '*')
        content = content.replace(']]', '*')

        # render to html
        content = content.replace('\\', '\\\\')
        out = markdown.markdown(content)

        # modify latex tags for anki to understand (mathjax)
        # https://docs.ankiweb.net/math.html
        inline_open = False
        display_open = False
        i = len(out)-1
        while i > 0:
            if out[i] == '$':
                if i == 0 or out[i-1] != '$': # inline
                    if inline_open:
                        out = out[:i] + '\\(' + out[i+1:]
                    else: # going back to front so add a '/' if open
                        out = out[:i] + '\\)' + out[i+1:]
                    inline_open = not inline_open
                elif i != 0: # display
                    if display_open:
                        out = out[:i-1] + '\\[' + out[i+1:]
                        i -= 2
                    else: # going back to front so add a '/' if open
                        out = out[:i-1] + '\\]' + out[i+1:]
                        i -= 2
                    display_open = not display_open
            i -= 1

        # TODO images--figure out with obsidian first


        deck.add_note(genanki.Note(
                model=genanki.BASIC_MODEL,
                fields=[filename[:-3], out]))
        n_cards += 1

# write the deck to a file
output_file = os.path.join(output_dir, f'{deck_name}.apkg')
genanki.Package(deck).write_to_file(output_file)
print(f'from directory {notes_dir} wrote {n_cards} cards to {output_file}')

# TODO can this be put directly in the anki files?

