import os
import re
import markdown
import genanki
import argparse


PREAMBLE_FILE = 'templates/mtpreamble.sty'


def get_mtpreamble_model(preamble_file=PREAMBLE_FILE):
    with open(preamble_file, 'r') as f:
        lines = f.readlines()

    preamble_text = '\\[\n'
    preamble_lines = [line.strip() for line in lines if 'newcommand' in line]
    for line in preamble_lines:
        preamble_text += line + '\n'
    preamble_text += '\\]'

    return genanki.Model(
            1273987212,
            'Basic (mtpreamble)',
            fields=[
                {
                    'name': 'Front',
                    'font': 'Arial',
                },
                {
                    'name': 'Back',
                    'font': 'Arial',
                },
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}' + '\n\n' + preamble_text,
                    'afmt': '{{Front}}\n\n<hr id=answer>\n\n{{Back}}' + '\n\n' + preamble_text,
                },
            ],
            css='.card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n')


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


def commit_buffer(buf: list[str]) -> str:
    out = ''
    for s in buf:
        out += s + '\n'
    return out.strip()


def add_card(
        deck: genanki.Deck,
        front: str,
        back: str,
        image_path=None,
        model=genanki.BASIC_MODEL,
        to_mathjax=True,
        add_latex_tags=False):
    if add_latex_tags:
        front = f'[latex]{front}[/latex]'
        back = f'[latex]{back}[/latex]'

    media = []
    front_html, front_media = to_html(front, image_path=image_path, to_mathjax=to_mathjax)
    back_html, back_media = to_html(back, image_path=image_path, to_mathjax=to_mathjax)
    media.extend(front_media)
    media.extend(back_media)

    deck.add_note(genanki.Note(
            model=model,
            fields=[front_html, back_html]))

    return media


def to_html(content: str, image_path=None, to_mathjax=True):
    """Convert from obsidian to html with anki specific formatting"""
    # deal with images
    media = []
    images = re.findall('!\[\[(.*?)\]\]', content)
    for image in images:
        if not image_path:
            print('called "to_html" without an image path with images in the content')
            exit(1)

        src = os.path.join(image_path, image)
        media.append(src)
        content = content.replace(
                f'![[{image}]]',
                f'![]({image})')

    # remove obsidian links
    content = content.replace('[[', '*')
    content = content.replace(']]', '*')

    # render to html
    content = content.replace('\\', '\\\\')
    out = markdown.markdown(content)

    # modify latex tags for anki to understand (mathjax)
    # https://docs.ankiweb.net/math.html
    if to_mathjax:
        inline_open = False
        display_open = False
        i = len(out)-1
        while i > 0:  # going back to front
            if out[i] == '$':
                if i == 0 or out[i-1] != '$':  # inline
                    if inline_open:
                        out = out[:i] + '\\(' + out[i+1:]
                    else:
                        out = out[:i] + '\\)' + out[i+1:]
                    inline_open = not inline_open
                elif i != 0: # display
                    if display_open:
                        out = out[:i-1] + '\\[' + out[i+1:]
                        i -= 2
                    else:
                        out = out[:i-1] + '\\]' + out[i+1:]
                        i -= 2
                    display_open = not display_open
            i -= 1

    return out, media
