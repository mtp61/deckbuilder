import os
import re
import markdown
import genanki


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
