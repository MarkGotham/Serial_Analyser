"""
===============================
Row Analyser (row_analyser.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Simple functions for investigating the properties of tone rows.

"""

from collections import Counter
from typing import Union, List, Tuple
import unittest

from music21 import chord
from music21 import serial


# ------------------------------------------------------------------------------

def getRowSegments(row: Union[List, serial.ToneRow],
                   overlapping: bool = True,
                   segmentLength: int = 3,
                   wrap: bool = True):
    """
    Takes a row's pitches and returns those pitches as a list of list of subsegments.

    Specifically, if overlapping is True (default), then this method returns each overlapping
    n-cardinality subsegment of a row where n is given by segmentLength.

    For instance, a segmentLength of 3 returns trichords of
    pitches 0,1,2 followed by 1,2,3 and so on.

    At the end of the row, if wrap is True (default) then the row wraps around to complete
    the final subsegments.
    For instance, continuing with trichords, this means the 11th and 12th trichords
    (pitches 9,10,11 followed by 10,11,0, and finally 11,0,1),

    [EXAMPLE IN TESTS]

    If wrap is set to False, the list stops at the end of the row proper
    (pitches 9,10,11), returning 10 trichords or equivalent.

    [EXAMPLE IN TESTS]

    If overlapping is set to False, then the row is divided instead into
    each discrete, non-overlapping n-cardinality subsegment.
    In this case, n must divide the row length without remainder.

    For instance, for 12-tone rows, a segmentLength of:

    * 2 returns 6 dyads (i.e. pitches 0,1 followed by 1,2 and so on);

    * 3 returns 4 trichords (i.e. pitches 0,1,2 followed by 3,4,5, and so on);

    * 4 return 3 tetrachords (pitches 0,1,2,3 followed by 4,5,6,7 and 8,9,10,11);

    * 6 return 2 hexachords (pitches 0,1,2,3,4,5 followed by 6,7,8,9,10,11).

    [EXAMPLE IN TESTS]

    """

    if not isinstance(row, List):
        if 'ToneRow' in row.classes:
            row = [n.pitch.pitchClassString for n in row]
        else:
            raise ValueError('The pitchList must be a list or a music21.serial.ToneRow')

    totalPitches = len(row)
    if segmentLength >= totalPitches:
        raise ValueError('The segmentLength must be less than that of the pitchList.')

    if overlapping:
        if wrap:
            row += row[:segmentLength - 1]
            totalPitches = len(row)

        nChords = []
        for i in range(totalPitches - (segmentLength - 1)):
            nChords.append(row[i:i + segmentLength])

    else:  # Discrete (not overlapping)
        steps = totalPitches / segmentLength

        if steps - int(steps) != 0:
            raise ValueError('The segmentLength must divide the number of pitches.')

        nChords = [row[i * segmentLength:(i + 1) * segmentLength] for i in range(int(steps))]

    return nChords


def containsCell(segmentsListOfLists: List,
                 exactlyOne: bool = True):
    """
    Having retrieved a set of subsegments using getRowSegments,
    check for multiple instances of a single pitch class set.

    Returns the repeated cell/s (as a pitch class string like '<012>') if found and
    nothing (False) if not.

    If exactlyOne is True (default), the result is only True and returned if
    all the sub-segments are instances of the same pitch class set.

    The primary intended use case here is for discrete subsegments of a 12-tone row but
    this can be called on overlapping segments or indeed on any other list of segments.
    """

    primeSegs = [chord.Chord(seg).primeFormString for seg in segmentsListOfLists]

    countDict = Counter(primeSegs)
    repeated = [x for x in countDict if countDict[x] > 1]

    if not repeated:
        return False
    if exactlyOne:
        if len(countDict) == 1:
            return repeated
        else:
            return False
    return repeated


def isSelfRI(row: Union[List, serial.ToneRow]):
    """
    True if the interval succession of a row is a palindrome.
    I.e. the interval succession is the same backwards and forwards.
    """

    if isinstance(row, list):
        row = serial.ToneRow(row)
    forwardIntvs = row.getIntervalsAsString()
    if forwardIntvs == forwardIntvs[::-1]:
        return True


# ------------------------------------------------------------------------------

# Combinatoriality

"""

This combinatoriality_dict maps all 50 hexachords 
(listed in Forte-class order, so 6-1, 6-2, ... ) 
to their combinatoriality status. There are 5 options:
'A' for all-combinatorial,
'T' for transposition only,
'I' for inversion only,
'RI' for retrograde-inversion only, and
'' (an empty string) for non-combinatorial. 

"""

combinatoriality_dict = {(0, 1, 2, 3, 4, 5): 'A',
                         (0, 1, 2, 3, 4, 6): 'I',
                         (0, 1, 2, 3, 5, 6): '',
                         (0, 1, 2, 4, 5, 6): 'RI',
                         (0, 1, 2, 3, 6, 7): 'I',
                         (0, 1, 2, 5, 6, 7): 'RI',
                         (0, 1, 2, 6, 7, 8): 'A',
                         (0, 2, 3, 4, 5, 7): 'A',
                         (0, 1, 2, 3, 5, 7): 'I',
                         (0, 1, 3, 4, 5, 7): '',
                         (0, 1, 2, 4, 5, 7): '',
                         (0, 1, 2, 4, 6, 7): '',
                         (0, 1, 3, 4, 6, 7): 'RI',
                         (0, 1, 3, 4, 5, 8): 'T',
                         (0, 1, 2, 4, 5, 8): 'I',
                         (0, 1, 4, 5, 6, 8): 'I',
                         (0, 1, 2, 4, 7, 8): '',
                         (0, 1, 2, 5, 7, 8): 'I',
                         (0, 1, 3, 4, 7, 8): '',
                         (0, 1, 4, 5, 8, 9): 'A',
                         (0, 2, 3, 4, 6, 8): 'I',
                         (0, 1, 2, 4, 6, 8): 'I',
                         (0, 2, 3, 5, 6, 8): 'RI',
                         (0, 1, 3, 4, 6, 8): '',
                         (0, 1, 3, 5, 6, 8): '',
                         (0, 1, 3, 5, 7, 8): 'RI',
                         (0, 1, 3, 4, 6, 9): 'I',
                         (0, 1, 3, 5, 6, 9): 'RI',
                         (0, 1, 3, 6, 8, 9): 'RI',
                         (0, 1, 3, 6, 7, 9): 'I',
                         (0, 1, 3, 5, 8, 9): 'I',
                         (0, 2, 4, 5, 7, 9): 'A',
                         (0, 2, 3, 5, 7, 9): 'I',
                         (0, 1, 3, 5, 7, 9): 'I',
                         (0, 2, 4, 6, 8, 10): 'A',
                         (0, 1, 2, 3, 4, 7): '',
                         (0, 1, 2, 3, 4, 8): 'RI',
                         (0, 1, 2, 3, 7, 8): 'RI',
                         (0, 2, 3, 4, 5, 8): '',
                         (0, 1, 2, 3, 5, 8): '',
                         (0, 1, 2, 3, 6, 8): '',
                         (0, 1, 2, 3, 6, 9): 'RI',
                         (0, 1, 2, 5, 6, 8): '',
                         (0, 1, 2, 5, 6, 9): '',
                         (0, 2, 3, 4, 6, 9): 'RI',
                         (0, 1, 2, 4, 6, 9): '',
                         (0, 1, 2, 4, 7, 9): '',
                         (0, 1, 2, 5, 7, 9): 'RI',
                         (0, 1, 3, 4, 7, 9): 'RI',
                         (0, 1, 4, 6, 7, 9): 'RI'}


def combinatorialType(row: Union[List, Tuple]):
    """
    Rows can be
    'semi-combinatorial' by one of transposition (T), inversion (I), or retrograde-inversion (RI);
    'all-combinatorial' (A) by all of those three;
    or 'non-combinatorial'.

    That status is given by their hexachords.
    For instance, there are exactly 6 unordered hexachords that are all-combinatorial:
    (0, 1, 2, 3, 4, 5),
    (0, 1, 2, 6, 7, 8),
    (0, 2, 3, 4, 5, 7),
    (0, 1, 4, 5, 8, 9),
    (0, 2, 4, 5, 7, 9), and
    (0, 2, 4, 6, 8, 10).

    This function provides a simple look up
    for any given row, returning the string of the status for combinatorial rows
    (one of T, I, RI, or A) or an empty string for non-combinatorial cases.
    """

    hexachord = row[:6]
    c = chord.Chord(hexachord)
    return combinatoriality_dict[tuple(c.primeForm)]


def combinatorialByTransform(row: serial.TwelveToneRow,
                             transformation: str,
                             return_types: bool = True):
    """
    Check if a row is combinatorial with itself by any or all of
    transposition, inversion, and retrograde-inversion.

    Unlike 'combinatorial lookup', this function works by
    comparing a row (assumed to by P0) with
    the user-defined transformation in each of the 12 transpositions.

    Returns False where there is no such combinatoriality.
    Where there is, the function returns the specific transposition(s) of the combinatorial pairs
    if return_types is set to True (default), or simply True if not.

    The transformation types are limited to
    'T' for transposition,
    'I' for inversion, and
    'RI' for retrograde-inversion
    (prime to retrograde combinatoriality is true by definition).
    """

    if transformation not in ['T', 'I', 'RI']:
        raise ValueError('Transformation must be '
                         '"T" for transposition, '
                         '"I" for inversion, '
                         'or "RI" for retrograde-inversion.')

    if return_types:
        returnMatch = []

    for i in range(12):
        if row.areCombinatorial('P', 0, transformation, i, 'zero'):
            if return_types:
                returnMatch.append(i)
            else:
                return True

    if return_types:
        return returnMatch


def allCombinatorialFullTypes(row: Union[List, serial.TwelveToneRow]):
    """
    Call on an 'all combinatorial' row.
    (Error raised if the row is not all-combinatorial.

    Returns the specific transpositions of each combinatoriality types in the form, for instance
    for teh chromatic scale: 'P0-P6; -I11; -RI5'.

    This works with cases of multiple matches per transformation. For instance
    Hale Smith's "Contours for Orchestra" row [0, 5, 6, 4, 10, 11, 7, 2, 1, 3, 9, 8],
    returns 'P0-P3,9; -I1,7; -RI4,10'.
    """

    if isinstance(row, list):
        pitchList = row
        row = serial.TwelveToneRow(pitchList)
    else:
        pitchList = [p.pitchClass for p in row.pitches]

    c = chord.Chord(pitchList[:6])
    if combinatorialType(tuple(c.primeForm)) != 'A':
        raise ValueError('This is not an all-combinatorial row.')

    p = ','.join([str(x) for x in combinatorialByTransform(row, 'T')])
    i = ','.join([str(x) for x in combinatorialByTransform(row, 'I')])
    ri = ','.join([str(x) for x in combinatorialByTransform(row, 'RI')])
    return f'P0-P{p}; -I{i}; -RI{ri}'


# ------------------------------------------------------------------------------

class SerialTester(unittest.TestCase):

    def testDiscreteAndCells(self):
        """
        Tests the retrieval of discrete subsegments of a row.

        The row in Webern's String Quartet, Op. 28 comprises 3x the same tetrachord.
        The containsCell function therefore returns a
        positive result for the 3 discrete tetrachords,
        but nothing (False) for the 4 discrete trichords,

        Conversely, Webern's Concerto for Nine Instruments (Konzert), Op. 24,
        comprises 4x the same trichord.
        """

        quartet = [0, 11, 2, 1, 5, 6, 3, 4, 8, 7, 10, 9]
        tetrachords = getRowSegments(quartet, overlapping=False, segmentLength=4)
        self.assertEqual(tetrachords, [[0, 11, 2, 1], [5, 6, 3, 4], [8, 7, 10, 9]])
        cells = containsCell(tetrachords)
        self.assertEqual(cells, ['<0123>'])

        trichords = getRowSegments(quartet, overlapping=False, segmentLength=3)
        self.assertEqual(trichords, [[0, 11, 2], [1, 5, 6], [3, 4, 8], [7, 10, 9]])
        self.assertFalse(containsCell(trichords))

        konzert = [0, 11, 3, 4, 8, 7, 9, 5, 6, 1, 2, 10]
        tetrachords = getRowSegments(konzert, overlapping=False, segmentLength=4)
        self.assertEqual(tetrachords, [[0, 11, 3, 4], [8, 7, 9, 5], [6, 1, 2, 10]])
        cells = containsCell(tetrachords)
        self.assertFalse(cells)

        trichords = getRowSegments(konzert, overlapping=False, segmentLength=3)
        self.assertEqual(trichords, [[0, 11, 3], [4, 8, 7], [9, 5, 6], [1, 2, 10]])
        self.assertEqual(containsCell(trichords), ['<014>'])

    def testAllTrichord(self):
        """
        Tests the retrieval of all (12), overlapping trichords from a 12-tone row.
        Tests the four distinct 'all-trichord rows' where every such trichord is different
        (and which therefor cover all the 12 distinct trichords between them).
        See Alan Marsden 2012 for a discussion and proof.
        """

        allTrichordRows = [[0, 2, 6, 10, 5, 3, 8, 9, 11, 7, 4, 1],
                           [0, 2, 6, 10, 11, 9, 8, 3, 5, 1, 4, 7],
                           [0, 2, 6, 10, 7, 4, 11, 9, 8, 3, 5, 1],
                           [0, 2, 6, 10, 1, 4, 5, 3, 8, 9, 11, 7]]

        for row in allTrichordRows:
            trichords = getRowSegments(row,
                                       overlapping=True,
                                       segmentLength=3,
                                       wrap=True)
            self.assertEqual(len(trichords), 12)
            cells = containsCell(trichords)  # checks for repeated cells
            self.assertFalse(cells)  # I.e. no repeated cells

    def testNoWrap(self):
        """
        Simple tests of the wrap = False condition for segments.
        """

        testRow = [x for x in range(12)]
        trichords = getRowSegments(testRow,
                                   overlapping=True,
                                   segmentLength=6,
                                   wrap=False)  # ***
        self.assertEqual(len(trichords), 7)

    def testSelfRI(self):
        """
        Simple test of the self-retrograde inversion function with the example of Dallapiccola's
        "Dialoghi" (which is) and
        "Piccola musica notturna" (which isn't).
        """

        rowDallapiccolaDialoghi = [0, 1, 10, 2, 6, 4, 5, 3, 7, 11, 8, 9]
        self.assertTrue(isSelfRI(rowDallapiccolaDialoghi))

        rowDallapiccolaPiccola = [0, 9, 1, 3, 4, 11, 2, 8, 7, 5, 10, 6]
        self.assertFalse(isSelfRI(rowDallapiccolaPiccola))

    def testCombinatorial(self):
        """
        Test one example case that is transposition-combinatorial (Elisabeth Lutyens' "Islands")
        and another that is inversion-combinatorial (Olly Wilson's "Piece for Four")
        neither of which is all-combinatorial.

        Then test three cases that are all-combinatorial: the chromatic scale,
        Klein's 'Mutter Chord' (better known from Berg's Lyric suite),
        and Hale Smith's "Contours for Orchestra".
        """

        rowLutyens = [0, 11, 7, 3, 8, 10, 9, 6, 4, 5, 1, 2]
        rowWilson = [0, 8, 9, 4, 2, 6, 7, 11, 10, 3, 5, 1]

        # Lutyens: transposition, not inversion
        self.assertEqual(combinatorialType(rowLutyens), 'T')
        self.assertTrue(combinatorialByTransform(serial.pcToToneRow(rowLutyens), 'T'))
        self.assertFalse(combinatorialByTransform(serial.pcToToneRow(rowLutyens), 'I'))

        # Wilson: inversion, not transposition
        self.assertTrue(combinatorialType(rowWilson), 'I')
        self.assertTrue(combinatorialByTransform(serial.pcToToneRow(rowWilson), 'I'))
        self.assertFalse(combinatorialByTransform(serial.pcToToneRow(rowWilson), 'T'))

        # Three all-combinatorial cases
        chromaticRow = [[x for x in range(12)], 'P0-P6; -I11; -RI5']
        rowBergKlein = [[0, 11, 7, 4, 2, 9, 3, 8, 10, 1, 5, 6], 'P0-P6; -I5; -RI11']
        rowSmith = [[0, 5, 6, 4, 10, 11, 7, 2, 1, 3, 9, 8], 'P0-P3,9; -I1,7; -RI4,10']

        for r in [chromaticRow, rowBergKlein, rowSmith]:
            self.assertEqual(combinatorialType(r[0]), 'A')
            row = serial.pcToToneRow(r[0])
            self.assertEqual(allCombinatorialFullTypes(row), r[1])


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
