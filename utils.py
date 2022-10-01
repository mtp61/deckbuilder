import os
import re
import markdown


OUTPUT_DIR_DEFAULT = os.path.expanduser('~/Downloads')


def to_html(content: str, image_path=None):
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
    inline_open = False
    display_open = False
    i = len(out)-1
    while i > 0: # going back to front
        if out[i] == '$':
            if i == 0 or out[i-1] != '$': # inline
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

