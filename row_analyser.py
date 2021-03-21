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
from typing import Union, List
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


def containsCell(segmentsListOfLists: List):
    """
    Having retrieved a set of subsegments using getRowSegments,
    check for multiple instances of a single pitch class set.

    Returns the repeated cell/s if found and nothing (False) if not.
    """

    primeSegs = [chord.Chord(seg).forteClass for seg in segmentsListOfLists]

    countDict = Counter(primeSegs)
    repeated = [x for x in countDict if countDict[x] > 1]
    if repeated:
        return repeated


def isSelfRetrograde(row: Union[List, serial.ToneRow]):
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

class SerialTester(unittest.TestCase):

    def testDiscreteAndCells(self):
        """
        Tests the retrieval of all (3) discrete tetrachords from a row.
        This row (Webern, String Quartet, Op. 28) comprises 3x the same tetrachord.
        """

        # Discrete
        r = [0, 11, 2, 1, 5, 6, 3, 4, 8, 7, 10, 9]
        tetrachords = getRowSegments(r,
                                     overlapping=False,
                                     segmentLength=4)
        self.assertEqual(tetrachords, [[0, 11, 2, 1], [5, 6, 3, 4], [8, 7, 10, 9]])

        # Cells
        cells = containsCell(tetrachords)
        self.assertEqual(cells, ['4-1'])

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

    def testSelfRetrograde(self):
        """
        Simple test of the self-retrograde function.
        """

        rowDallapiccolaDialoghi = [0, 1, 10, 2, 6, 4, 5, 3, 7, 11, 8, 9]
        self.assertTrue(isSelfRetrograde(rowDallapiccolaDialoghi))


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
