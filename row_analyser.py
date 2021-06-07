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

Functions for investigating the properties of tone rows, centered on:
- sub-segments for derived rows, and
- combinatoriality properties

"""

from collections import Counter
from typing import Union, List, Tuple
import unittest

import transformations
import pc_sets


# ------------------------------------------------------------------------------

def getRowSegments(row: Union[List, Tuple],
                   overlapping: bool = True,
                   segmentLength: int = 3,
                   wrap: bool = True):
    """
    Takes a row's pitches and returns those pitches as a list of list of sub-segments.

    Specifically, if overlapping is True (default), then this method returns each overlapping
    n-cardinality sub-segment of a row where n is given by segmentLength.

    For instance, a segmentLength of 3 returns trichords of
    pitches 0,1,2 followed by 1,2,3 and so on.

    At the end of the row, if wrap is True (default) then the row wraps around to complete
    the final sub-segments.
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
            raise ValueError(f'When not overlapping, segmentLength (currently {segmentLength}) '
                             f'must divide the number of pitches (currently {totalPitches}).')

        nChords = [row[i * segmentLength:(i + 1) * segmentLength] for i in range(int(steps))]

    return nChords


def containsCell(segmentsListOfLists: List,
                 exactlyOne: bool = True):
    """
    Having retrieved a set of sub-segments (for instance using row_basics.getRowSegments),
    check for multiple instances of a single pitch class set.

    Returns the repeated cell/s as a tuple like '(0, 1, 2)' if found and
    nothing (False) if not.

    If exactlyOne is True (default), the result is only True and returned if
    all the sub-segments are instances of the same pitch class set.

    The primary intended use case here is for discrete sub-segments of a 12-tone row but
    this can be called on overlapping segments or indeed on any other list of segments.
    """

    primeSegs = [str(pc_sets.pitchesToPrime(seg)) for seg in segmentsListOfLists]

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


# ------------------------------------------------------------------------------

def isSelfRotational(segmentsListOfLists: List):
    """
    True in the very rare case that a row is rotation symmetrical.
    This is a sub-property of derived rows.
    Call on a derived row expressed as a segmentListOfLists in the same way as for `containsCell`.

    This function will first confirm the derivation at that segment size by calling `containsCell`
    and then check for rotational symmetry.
    After all that, it's still pretty unlikely to come back True;
    all the more notable then when it does!
    """
    if containsCell(segmentsListOfLists, exactlyOne=True):
        referenceInterval = (segmentsListOfLists[0][0] - segmentsListOfLists[1][0]) % 12
        for index in range(len(segmentsListOfLists) - 1):
            segment = segmentsListOfLists[index]
            for i in range(len(segment)):
                interval = (segment[i] - segmentsListOfLists[index + 1][i]) % 12
                if interval != referenceInterval:
                    return False
        return True
    else:
        raise ValueError('Not a valid (derived) row')


def is12tone(row: Union[List, Tuple]):
    """
    Simple check whether a row is 12-tone.
    Specifically, returns True if the row is
    12 notes long (not shorter or longer) and
    there are no duplicated pitches within the 12.
    """
    return sorted(row) == list(range(12))


def isAllInterval(row: Union[List, Tuple],
                  require12tone: bool = True):
    """
    True / False for the all-interval property (i.e. uses each interval class 1–11).
    If require12tone is True (default) then 12-tone row (each interval exactly once).
    """

    if require12tone:
        if not is12tone(row):
            return False

    intervals = transformations.pitchesToIntervals(row)
    for x in range(1, 12):
        if x not in intervals:
            return False

    return True


def isSelfR(row: Union[List, Tuple]):
    """
    True if the retrograde of a row is transposition-equivalent to the prime.
    """

    r0 = row[::-1]
    r_t0 = transformations.transposeTo(r0, 0)

    if row == r_t0:
        return True


def isSelfRI(row: Union[List, Tuple]):
    """
    True if the interval succession of a row is a palindrome.
    I.e. the interval succession is the same backwards and forwards.
    """

    intervals = transformations.pitchesToIntervals(row)
    if intervals == intervals[::-1]:
        return True


# ------------------------------------------------------------------------------

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

    hexachord = tuple(row[:6])
    vector = pc_sets.pitchesToIntervalVector(hexachord)
    return pc_sets.intervalVectorToCombinatoriality(vector)


def combinatorialPair(row1: Union[List, Tuple],
                      row2: Union[List, Tuple]):
    """
    True / False for whether any input pair of rows is combinatorial.
    """
    for row in [row1, row2]:
        if len(row) != 12:
            raise ValueError('This function is designed for 12-tone rows')
    newRow = sorted(row1[:6] + row2[:6])
    return newRow == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def combinatorialByTransform(row: Union[List, Tuple],
                             transformation: str,
                             returnTypes: bool = True):
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

    if returnTypes:
        returnMatch = []

    comparisonRow = [x for x in row]
    if transformation in ['I', 'RI']:
        comparisonRow = transformations.invert(comparisonRow)
        if transformation == 'RI':
            comparisonRow = transformations.retrograde(comparisonRow)

    for i in range(12):
        comparisonRow = transformations.transposeBy(comparisonRow, 1)
        if combinatorialPair(comparisonRow, row):
            if returnTypes:
                returnMatch.append(i + 1)  # NB
            else:
                return True

    if returnTypes:
        return returnMatch


def fullCombinatorialTypes(row: Union[List, Tuple],
                           returnAsString: bool = True):
    """
    Returns the specific transpositions of each combinatoriality types by reference to P0.
    If returnAsString is True (default) then this function returns
    a string combining all cases.
    For instance, the chromatic scale [0, 1, 2, ...] returns 'T6; I11; RI5'
    Otherwise, (returnAsString is False) a dict is returns with keys for 'T', 'I', and 'RI'
    and values as lists with the transpositions for each, such as
    {'T': [6], 'I': [11], 'RI': [5]} for that chromatic scale.

    This works with cases of multiple matches per transformation. For instance
    Hale Smith's "Contours for Orchestra" row [0, 5, 6, 4, 10, 11, 7, 2, 1, 3, 9, 8]
    returns 'T3,9; I1,7; RI4,10' or {'T': [3, 9], 'I': [1, 7], 'RI': [4, 10]}.

    For non-combinatorial cases the string (or dict's value lists) are returned empty.

    Accepts rows as a list of pitch classes.
    """

    outDict = {}
    for transform in ['T', 'I', 'RI']:
        outDict[transform] = [x for x in combinatorialByTransform(row, transform)]

    if returnAsString:
        outList = []
        for transform in ['T', 'I', 'RI']:
            if outDict[transform]:
                outList.append(transform + ','.join([str(x) for x in outDict[transform]]))
        return '; '.join(outList)

    else:
        return outDict


# ------------------------------------------------------------------------------

class SerialTester(unittest.TestCase):

    def testDiscreteAndCells(self):
        """
        Tests the retrieval of discrete sub-segments of a row.

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
        self.assertEqual(cells, ['(0, 1, 2, 3)'])

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
        self.assertEqual(containsCell(trichords), ['(0, 1, 4)'])

    def testAllTrichord(self):
        """
        Tests the retrieval of all (12), overlapping trichords from a 12-tone row.
        Tests the four distinct 'all-trichord rows' where every such trichord is different
        (and which therefore cover all the 12 distinct trichords between them).
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

    def testSelfRotational(self):
        """
        Test self-rotationality on Lutosławski's Musique Funébre (Funeral Music) row in both
        segments of size 2 (true) and 3 (false).
        """
        luto2 = [[0, 6], [5, 11], [10, 4], [3, 9], [8, 2], [1, 7]]
        luto3 = [[0, 6, 5], [11, 10, 4], [3, 9, 8], [2, 1, 7]]
        self.assertTrue(isSelfRotational(luto2))
        self.assertFalse(isSelfRotational(luto3))

    def testIs12tone(self):
        """
        True if the row is 12 notes long (not shorter or longer) and
        there are no duplicated pitches within the 12.
        Test one case of each case.
        """

        chromaticRow = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.assertTrue(is12tone(chromaticRow))

        halfChromaticRow = chromaticRow[0:6]
        doubleChromaticRow = chromaticRow * 2
        pitchDuplicate = [10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.assertFalse(is12tone(halfChromaticRow))
        self.assertFalse(is12tone(doubleChromaticRow))
        self.assertFalse(is12tone(pitchDuplicate))

    def testSelfRIAndAllInterval(self):
        """
        Test of the all-interval and self-retrograde inversion functions with the example of
        Dallapiccola's
        "Dialoghi" (which is self-retrograde inverse but not all-interval) and
        "Piccola musica notturna" (which is all-interval but isn't self-retrograde inverse).
        """

        rowDallapiccolaDialoghi = [0, 1, 10, 2, 6, 4, 5, 3, 7, 11, 8, 9]
        self.assertTrue(isSelfRI(rowDallapiccolaDialoghi))
        self.assertFalse(isAllInterval(rowDallapiccolaDialoghi))

        rowDallapiccolaPiccola = [0, 9, 1, 3, 4, 11, 2, 8, 7, 5, 10, 6]
        self.assertFalse(isSelfRI(rowDallapiccolaPiccola))
        self.assertTrue(isAllInterval(rowDallapiccolaPiccola))

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
        self.assertTrue(combinatorialByTransform(rowLutyens, 'T'))
        self.assertFalse(combinatorialByTransform(rowLutyens, 'I'))

        # Wilson: inversion, not transposition
        self.assertTrue(combinatorialType(rowWilson), 'I')
        self.assertTrue(combinatorialByTransform(rowWilson, 'I'))
        self.assertFalse(combinatorialByTransform(rowWilson, 'T'))

        # Three all-combinatorial cases
        chromaticRow = [[x for x in range(12)], 'T6; I11; RI5']
        rowBergKlein = [[0, 11, 7, 4, 2, 9, 3, 8, 10, 1, 5, 6], 'T6; I5; RI11']
        rowSmith = [[0, 5, 6, 4, 10, 11, 7, 2, 1, 3, 9, 8], 'T3,9; I1,7; RI4,10']

        for r in [chromaticRow, rowBergKlein, rowSmith]:
            self.assertEqual(combinatorialType(r[0]), 'A')
            self.assertEqual(fullCombinatorialTypes(r[0]), r[1])

    def testCombinatoriality(self):

        # Invariance:
        sum_inv = sum([x[3] for x in pc_sets.hexachords])
        self.assertEqual(sum_inv, 924)  # 12! / 6!*6!

        # Combinatoriality:
        for entry in pc_sets.hexachords:
            hexachord = entry[1]
            complement = tuple([x for x in range(12) if x not in hexachord])
            row = list(hexachord) + list(complement)
            query = fullCombinatorialTypes(row, returnAsString=False)
            combType = entry[-1]
            if combType == 'A':
                self.assertTrue(query['T'])
                self.assertTrue(query['I'])
                self.assertTrue(query['RI'])
            elif combType == 'T':
                self.assertTrue(query['T'])
                self.assertFalse(query['I'])
                self.assertFalse(query['RI'])
            elif combType == 'I':
                self.assertFalse(query['T'])
                self.assertTrue(query['I'])
                self.assertFalse(query['RI'])
            elif combType == 'RI':
                self.assertFalse(query['T'])
                self.assertFalse(query['I'])
                self.assertTrue(query['RI'])


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
