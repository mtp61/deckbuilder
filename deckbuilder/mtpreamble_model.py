import genanki


PREAMBLE_FILE = '../templates/mtpreamble.sty'


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
