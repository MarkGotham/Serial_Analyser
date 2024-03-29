"""
===============================
Anthology Script Generator (anthology_script_generator.py)
===============================

Mark Gotham


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Simple script for running the relevant retrieval functions from row_analyser.py
and generating the textbook anthology chapter script in html.

Creates dicts with header, explanation, and list of instances for printing.

"""

# ------------------------------------------------------------------------------

import row_analyser
import pc_sets

import json
from typing import List, Dict
from pathlib import Path


# ------------------------------------------------------------------------------

def load_corpus(
        path: Path = Path('Repertoire_Anthology') / 'rows_in_the_repertoire.json'
) -> list:
    with open(path) as f:
        return json.load(f)


# ------------------------------------------------------------------------------

def retrieve_instances(
        data: list
) -> list:
    """
    Reads off row properties (see `.add_properties()`) and prepares dicts for html.
    Also runs the special case of re-used rows (not handled by `.add_properties()`).
    """

    # Initialise dicts
    reused = {'header': 'Re-used Rows',
              'explanation': 'We begin with rows used more than once in this collection. '
                             'This takes account of transposition (by comparing P0 forms), '
                             'but not inversion or retrograde equivalence. '
                             'This list is short and largely '
                             'limited to "famous" rows like the '
                             'so-called "mother" chord (Berg, Ginastera, Klein) and '
                             'cases of homage such as '
                             'the Boulez-Messiaen and Payne-Lutyens pairs.',
              'list': []
              }

    allInterval = {'header': 'All-Interval',
                   'explanation': 'All-interval rows go through all 11 different intervals '
                                  '(1, 2, 3, ... 11) between neighbouring pitches in the row.',
                   'list': []
                   }

    selfR = {'header': 'Self Retrograde',
             'explanation': 'We turn now to classes of row symmetry, beginning with '
                            'self retrograde rows for which '
                            'the prime form is transposition-equivalent to its retrograde. '
                            'The section after this one deals with retrograde inversion symmetry, '
                            'and rotational symmetry is included as part of the following '
                            'sections on derived rows (starting with "6x Same Dyad").',
             'list': []
             }

    selfRI = {'header': 'Self Retrograde Inversion',
              'explanation': 'These rows have a palindromic interval succession meaning that '
                             'the prime is transposition-equivalent to its retrograde-inversion.',
              'list': []
              }

    dyads = {'header': '6x Same Dyad (interval)',
             'explanation': 'These next four sections set out cases where the '
                            'discrete sub-segments of a row all form the same pitch class set. '
                            'The pitch class set in question is given after the row '
                            'in prime form and rows which are also self-rotational are '
                            'identified (with the self-rotational interval pattern). '
                            'This first section presents cases of 6x the same dyad '
                            '(pitches 1-2, 3-4, 5-6, 7-8, 9-10, and 11-12).',
             'list': []
             }

    trichords = {'header': '4x Same Trichord',
                 'explanation': 'Now for cases of 4x the same trichord '
                                '(pitches 1-3, 4-6, 7-9 and 10-12).',
                 'list': []
                 }

    tetrachords = {'header': '3x Same Tetrachord',
                   'explanation': 'Next up we have cases of 3x the same tetrachord '
                                  '(pitches 1-4, 5-8, and 8-12).',
                   'list': []
                   }

    hexachords = {'header': '2x Same Hexachord',
                  'explanation': 'Finally, we have the relatively common condition of '
                                 '2x the same hexachord (pitches 1-6 and 7-12).',
                  'list': []
                  }

    tCombinatorial = {'header': 'Transposition Combinatorial',
                      'explanation': 'When two rows are combinatorial, the '
                                     'first hexachord of each complements the other '
                                     'meaning that they make up the total chromatic together. '
                                     'This list gives rows in this section that are combinatorial '
                                     'by transposition, i.e. '
                                     'combinatoriality holds between P0 and '
                                     'at least one transposition of P. '
                                     'The transposition(s) are given after the row. '
                                     'In this case, there is only one transposition-combinatorial '
                                     'hexachord, and only one interval, so they are all P0-P6',
                      'list': []
                      }

    iCombinatorial = {'header': 'Inversion Combinatorial',
                      'explanation': 'These rows are combinatorial by inversion. '
                                     'There are 13 such hexachords and some are combinatorial in '
                                     'more that one transposition, so '
                                     'the specific forms are given in the form '
                                     'P0-IX, or P0-IX,Y in the case of more than one match.',
                      'list': []
                      }

    riCombinatorial = {'header': 'Retrograde Inversion Combinatorial',
                       'explanation': 'These rows are combinatorial by retrograde inversion.',
                       'list': []
                       }

    allCombinatorial = {'header': 'All-Combinatorial',
                        'explanation': 'Finally, rows are all-combinatorial when the '
                                       'combinatorial property holds '
                                       'for all transformations '
                                       'in at least one transposition. '
                                       'Notice how the whole-tone hexachord [0,2,4,6,8,10] '
                                       '(in any ordering) '
                                       'stands out for its highly combinatorial properties.',
                        'list': []
                        }

    p0dict = {}  # Special case for re-used

    interval_pattern_list = []

    for x in data:

        entry = data[x]

        row = entry['P0']  # Used below. Here to check it's 12-tone

        basicString = f"{entry['Composer']}: {entry['Work']}"

        # Special case for re-used. TODO currently only P0 match: do I, R, RI as well
        if str(row) in p0dict:
            p0dict[str(row)].append(basicString)
        else:
            p0dict[str(row)] = [basicString]

        basicString += f", {row}"  # For all except re-used, handled already

        # Derived
        for segment in [(dyads, 2), (trichords, 3), (tetrachords, 4), (hexachords, 6)]:
            d = row_analyser.derived(row, segment[1])
            if d:
                extendedString = f'{basicString}, pc set {d[0]}'
                if len(d) > 1:
                    extendedString += f', self-rotational interval pattern {d[1]}'
                segment[0]['list'].append(extendedString)
                if len(d) > 1:
                    break

        if row_analyser.isAllInterval(row):
            allInterval['list'].append(basicString)

        if row_analyser.isSelfR(row):
            selfR['list'].append(basicString)

        if row_analyser.isSelfRI(row):
            selfRI['list'].append(basicString)

        if row_analyser.combinatorialType(row) == 'A':
            allCom = row_analyser.fullCombinatorialTypes(row)
            prime = pc_sets.pitchesToPrime(row[:6])
            allCombinatorial['list'].append(f'{basicString}, {allCom}, {prime}')
        else:
            t = row_analyser.combinatorialByTransform(row, transformation='T')
            if t:
                trans = ','.join([str(x) for x in t])
                tCombinatorial['list'].append(basicString + f', P0-P{trans}')
            else:
                i = row_analyser.combinatorialByTransform(row, transformation='I')
                if i:
                    trans = ','.join([str(x) for x in i])
                    iCombinatorial['list'].append(basicString + f', P0-I{trans}')
                else:
                    ri = row_analyser.combinatorialByTransform(row, transformation='RI')
                    if ri:
                        trans = ','.join([str(x) for x in ri])
                        riCombinatorial['list'].append(basicString + f', P0-RI{trans}')

    for k in p0dict:  # Special case for re-used
        v = p0dict[k]
        if len(v) > 1:
            reused['list'].append(f'{k}: {"; ".join([y for y in v])}')

    return [reused, allInterval,
            selfR, selfRI,
            dyads, trichords, tetrachords, hexachords,
            tCombinatorial, iCombinatorial, riCombinatorial, allCombinatorial]


# ------------------------------------------------------------------------------

def write_html(dicts: List[Dict]):
    preamble = ['<header class="site-header">',
                '<div class="wrap">',
                f'The full list of rows above presents examples of repertoire row usages.',
                'The following sections interpret that list somewhat, '
                'looking for the presence of certain properties. '
                'For a longer introduction to what these properties mean, '
                'please see the Row Properties chapter.'
                ]

    with open('Repertoire_Anthology/Serial_Anthology.html', "w") as text_file:

        for x in preamble:
            text_file.write(x + '\n')

        for subject in dicts:
            text_file.write('<div>' + '\n')
            text_file.write(f"<h2>{subject['header']}</h2>" + '\n')
            text_file.write(subject['explanation'] + '\n')
            text_file.write('<ol>' + '\n')
            for x in subject['list']:
                text_file.write(f'<li>{x}' + '\n')
            text_file.write('</ol>' + '\n')
            text_file.write('</div>' + '\n')


# ------------------------------------------------------------------------------

def run_all():
    data = load_corpus()
    data = retrieve_instances(data)
    write_html(data)


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    run_all()
