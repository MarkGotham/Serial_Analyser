"""
===============================
List Processing (list_processing.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Simple scripts for processing the dataset.

Mostly conversions to create the versions in:
- csv format ('writeCSV')
- musical notation ('makeRowScore', NB: requires the external library music21)

Also to
- filter the list by one of the dict keys e.g. all by a specific composer ('filterByKey')
- retrieve all distinct sources ('getSources')
- deal with the various methods of writing rows with strings, lists, etc ('standardiseRow')

"""


# ------------------------------------------------------------------------------

import csv
import os
import json
import unittest

from typing import Optional, Union

import row_analyser


# ------------------------------------------------------------------------------

def writeCSV(
        keysToUse: Optional[list] = None,
        pathToJson: Optional[list] = None,
        pathToCsv: Optional[list] = None,
        numberPitchIndices: bool = True
) -> None:
    """
    Writes a csv representation of the main, json file. 
    The keysToUse parameter allows the user to how much of the data to transfer
    (as a list of relevant keys in the dict).
    The row (in P0 form) is assumed.
    Beyond that, the default is to include ['Composer', 'Work', 'Year'] only.
    """

    if keysToUse is None:
        keysToUse = ['Composer', 'Work', 'Year']  # NB: row assumed
    if pathToJson is None:
        pathToJson = ['.', 'Repertoire_Anthology', 'rows_in_the_repertoire.json']
    if pathToCsv is None:
        pathToCsv = ['.', 'Repertoire_Anthology', 'rows_in_the_repertoire.csv']

    jsonPath = os.path.join(*pathToJson)

    with open(jsonPath, 'r') as jsonFile:

        data = json.load(jsonFile).values()

        data = sorted(data, key=lambda k: (k['Composer'], k['Work']))

        csvPath = os.path.join(*pathToCsv)
        with open(csvPath, 'w') as csvFile:
            csvOut = csv.writer(csvFile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)

            headers = [x for x in keysToUse]
            if numberPitchIndices:
                headers += list(range(1, 13))

            csvOut.writerow(headers)

            for entry in data:
                to_write = [entry[x] for x in keysToUse]  # fails if invalid header
                if numberPitchIndices:
                    [to_write.append(x) for x in entry['P0']]
                else:
                    to_write.append(entry['P0'])
                csvOut.writerow(to_write)


# ------------------------------------------------------------------------------

def makeRowScore(
        data: Optional = None,
        write: bool = True,
        properties: bool = True,
        title: Optional[str] = 'Rows in the Repertoire'
):
    """
    Makes a score setting out any number of rows in musical notation,
    annotated with labelled pitch classes and work metadata (title, composer etc).

    Note: unlike the rest of this repository, this requires an external music21: library
    """

    from music21 import bar, expressions, layout, metadata, meter, serial, stream

    score = stream.Score()
    part = stream.Part()
    part.insert(0, meter.TimeSignature('12/4'))  # Not essential
    count = 1

    if not data:
        jsonPath = os.path.join('.', 'Repertoire_Anthology', 'rows_in_the_repertoire.json')
        with open(jsonPath) as jsonFile:
            data = json.load(jsonFile).values()

    for entry in data:  # dict
        m = stream.Measure(number=count)
        count += 1
        row = serial.pcToToneRow(entry['P0'])

        for x in row.notes:
            x.stemDirection = 'none'
            x.lyric = x.pitch.pitchClass
            m.insert(x.offset, x)

        # Composer
        te = entry['Composer'] + ": \n"

        # Work
        if len(entry['Work']) > 85:
            te += entry['Work'][:85] + " ..."
        else:
            te += entry['Work']

        # Year
        if entry["Year"]:
            te += f' ({entry["Year"]})'

        if properties:
            te += '\n' + makePropertiesString(entry['P0'])

        te = expressions.TextExpression(te)
        te.placement = "above"  # NB does not convert
        m.insert(0, te)

        part.append(m)

    score.append(part)

    # Layout
    for thisMeasure in score.parts[0].getElementsByClass('Measure'):
        thisMeasure.insert(bar.Barline(type='final', location='right'))
        thisMeasure.insert(layout.SystemLayout(isNew=True))

    # Metadata
    score.insert(0, metadata.Metadata())
    score.metadata.composer = 'Various composers and analysts, compiled by Mark Gotham'
    score.metadata.title = title

    if write:
        w = os.path.join('.', 'Repertoire_Anthology', title.replace(" ", "_") + '.mxl')
        score.write(fmt='mxl', fp=w)

    return score


def makePropertiesString(
        row: list
) -> str:
    """
    Prepare a string summary of row properties for inclusion in the musical rendering.
    # TODO further refactor what is shared with anthology script
    """
    these_properties = []

    # Derived
    for segmentLength in [2, 3, 4, 6]:
        d = row_analyser.derived(row, segmentLength)
        if d:
            these_properties.append(f'{segmentLength}-note cell {d[0].replace(" ", "")}')
            if len(d) > 1:
                these_properties.append(f'Self-rotational {d[1]}')
                break

    comb = row_analyser.fullCombinatorialTypes(row)
    if comb:
        these_properties.append("Combinatorial by " + comb)

    if row_analyser.isSelfR(row):
        these_properties.append("Self-retro.")

    if row_analyser.isSelfRI(row):
        these_properties.append("Self-retro.inv.")

    if row_analyser.isAllInterval(row):
        these_properties.append("All-interval")

    if row_analyser.isAllTrichord(row):
        these_properties.append("All-trichord")

    if these_properties:
        if len(these_properties) > 5:  # there are a few!
            print(row, these_properties)
            return "; \n".join(these_properties)
        else:
            return "; ".join(these_properties)
    else:
        return "(No properties to report)"


# ------------------------------------------------------------------------------

# Filtered information

def filterByKey(dictKey: str = 'Composer',
                dictValue: str = 'Lutyens, Elizabeth',
                exactCaseMatch: bool = True,
                title: str = '',
                score: bool = False,
                ):
    """
    Filter the overall list for entries of a particular kind defined by:
    dictKey: one of the attributes recorded in the dataset (e.g. 'Composer');
    dictValue: the value of that attribute (e.g. 'Lutyens, Elisabeth').

    The comparison is case-sensitive unless 'exactCaseMatch' is false.
    """

    jsonPath = os.path.join('.', 'Repertoire_Anthology', 'rows_in_the_repertoire.json')

    with open(jsonPath, 'r') as jsonFile:
        data = json.load(jsonFile).values()

        if exactCaseMatch:
            filtered_data = [x for x in data if x[dictKey] == dictValue]
        else:
            filtered_data = [x for x in data if (dictValue.lower() in x[dictKey].lower())]

    if score:
        if not title:
            title = f'{dictValue}_Rows'
        makeRowScore(filtered_data, write=True, title=title)

    return filtered_data


def getSources():
    """
    Retrieve all cite keys from the 'Source' field of each entry
    (and removing page numbers etc.).
    Returns an alphabetically sorted list of distinct entries.
    """

    p = os.path.join('.', 'Repertoire_Anthology', 'rows_in_the_repertoire.json')

    sources = []

    with open(p, 'r') as json_file:
        data = json.load(json_file).values()

        for x in data:
            theseSources = x['Source'].split('; ')
            sourcesSansPages = [x.split(',')[0] for x in theseSources]
            for s in sourcesSansPages:
                sources.append(s)

    return sorted(list(set(sources)))


# ------------------------------------------------------------------------------

def stringToPC(pitchString: str):
    """
    Converts a string like 'Bb' to the corresponding pc integer (10).

    First character must be one of the unmodified pitches: C, D, E, F, G, A, B
    (not case sensitive).

    Any subsequent characters must indicate a single accidental type: one of
    '♭', 'b' or '-' for flat;
    '♯', '#', and '+' for sharp.

    >>> es = 'Eb'
    >>> stringToPC(es)
    3

    >>> eses = 'Ebb'
    >>> stringToPC(eses)
    2

    Note that 's' is not a supported accidental type as it is ambiguous:
    'Fs' probably indicates F#, but Es is more likely Eb (German).

    Also unsupported:
     mixtures of sharps and flats (e.g. B#b);
     symbols for double sharps etc.;
     any other symbols (including white space).
    """

    # Four conditions

    # 1: type
    if type(pitchString) != str:
        raise TypeError('Invalid pitchString: must be a string')

    # 2: base pitch
    basePitches = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    pitchString = pitchString.lower()
    if pitchString[0] not in basePitches:
        raise ValueError(f'Invalid first character: must be one of {basePitches}.')

    # 3: valid accidental
    modifier = 0
    if len(pitchString) > 1:
        accidental = pitchString[1]
        if accidental in ['♭', 'b', '-']:
            modifier = -1
        elif accidental in ['♯', '#', '+']:
            modifier = +1
        else:
            raise ValueError('Invalid second character: must be an accidental.')

    # 4: same accidental
    if len(pitchString) > 2:
        for x in pitchString[2:]:
            assert (x == accidental)
        modifier *= len(pitchString) - 1

    initialDict = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}

    return initialDict[pitchString[0]] + modifier % 12


def standardiseRow(row: Union[str, list],
                   t0: bool = True,
                   ):
    """
    Accepts various representation of a row (as a list or a string in many different formats)
    and attempt to return a corresponding list of pitch classes.

    If t0 is True (default), then the return list is transposed to start on 0.

    See the tests for examples.
    """

    rowList = None

    if type(row) == list:
        if len(row) == 12:
            rowList = row
        elif len(row) == 1:
            row = row[0]
            if isinstance(row, list):
                rowList = row
        else:
            raise ValueError(f'Row list {row} invalid: must be of len 12 or 1.')

    if not rowList and isinstance(row, str):  # then convert it into a list

        for x in ['\n', '[', ']', '<', '>', '(', ')']:  # remove
            row = row.replace(x, '')

        dividers = [', ', ',', ' ', '~', '-', '–']  # split by
        # NB: order matters:
        # ', ' before ',' or ' ' and
        # last two (different) are potentially ambiguous: may indicate flat
        for divider in dividers:
            if divider in row:
                rowList = row.split(divider)
                break  # Assume only one and avoid '-' if possible.

        if not rowList:  # last try assuming no-divider notation e.g. 014295B38A76
            rowList = list(row)  # ['0', '1', '4', '2', '9', '5', 'B', '3', '8', 'A', '7', '6']

    # Now a list, convert each str element to int, directly or via stringToPC.
    assert isinstance(rowList, list)

    strCount = 0

    for x in range(len(rowList)):
        try:  # str of an int e.g., "0"
            rowList[x] = int(rowList[x])
        except:  # Actually a string. NB: may be pitch names or 'a, b' or 't, e' case
            strCount += 1

    if strCount == 0:  # all ints
        pass

    elif strCount == 2:  # 2 non-ints = 'a, b' or 't, e' case
        # Mixed case of (mostly) ints + 'a, b' or 't, e'.
        for x in range(len(rowList)):
            if not isinstance(rowList[x], int):
                assert isinstance(rowList[x], str)
                assert rowList[x].lower() in ['a', 'b', 't', 'e']
                if rowList[x].lower() in ['a', 't']:
                    rowList[x] = 10
                elif rowList[x].lower() in ['b', 'e']:
                    rowList[x] = 11

            assert isinstance(rowList[x], int)  # should now be done

    elif strCount == 12:  # all strings indicates pitch names
        for x in range(len(rowList)):
            rowList[x] = stringToPC(rowList[x])

    else:
        raise ValueError('Unrecognised format.')

    if t0:
        return [(x - rowList[0]) % 12 for x in rowList]
    else:
        return [x % 12 for x in rowList]


# ------------------------------------------------------------------------------

class ListTester(unittest.TestCase):

    def testStringToPC(self):
        pairs = (('Cbb', 10), ('C♭♭', 10), ('C--', 10),
                 ('Cb', 11), ('C♭', 11), ('C-', 11),
                 ('C', 0),
                 ('C#', 1), ('C♯', 1), ('C+', 1),
                 ('C##', 2), ('C♯♯', 2), ('C++', 2),
                 )
        for p in pairs:
            self.assertEqual(stringToPC(p[0]), p[1])

    def testStandardiseRow(self):
        """
        Tests some of the supported formats rationalised by standardiseRow:
         string of ints with <> angle brackets and '-' dividers,
         string of strings no brackets and ',' dividers,
         list of ints (requires only transposition), and
         list of strings.
        """

        GerhardConcerto = ('<0-4-1-11-10-3-6-5-9-8-2-7>',
                           [0, 4, 1, 11, 10, 3, 6, 5, 9, 8, 2, 7])
        LutyensTheNumbered = ('G#,F#,G,A,Bb,F,B,C,E,C#,Eb,D',
                              [0, 10, 11, 1, 2, 9, 3, 4, 8, 5, 7, 6])
        MorrisNotLilacs = ('014295B38A76',
                           [0, 1, 4, 2, 9, 5, 11, 3, 8, 10, 7, 6])
        SmithEvocation = ([9, 10, 4, 11, 6, 2, 5, 0, 7, 8, 1, 3],
                          [0, 1, 7, 2, 9, 5, 8, 3, 10, 11, 4, 6])
        WalkerSpatials = ('1 4 t 0 3 9 8 6 5 2 e 7',
                          [0, 3, 9, 11, 2, 8, 7, 5, 4, 1, 10, 6])
        WebernKonzert = (['11', '10', '2', '3', '7', '6', '8', '4', '5', '0', '1', '9'],
                         [0, 11, 3, 4, 8, 7, 9, 5, 6, 1, 2, 10])

        for entry in [GerhardConcerto, LutyensTheNumbered, MorrisNotLilacs,
                      SmithEvocation, WalkerSpatials, WebernKonzert]:
            self.assertEqual(standardiseRow(entry[0]), entry[1])

    def testSources(self):
        s = getSources()
        self.assertEqual(s[0], 'Ahrend2006')
        self.assertEqual(len(s), 149)


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
