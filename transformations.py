"""
===============================
Transformations (transformations.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Functions for transforming pitch lists like tone rows:
transposition, inversion, retrograde, rotation,
and a couple of more niche operations.

"""

from typing import Union, List, Tuple
import unittest


# ------------------------------------------------------------------------------

# Basic operations first: transpose, retrograde, invert.

def transposeBy(
        row: Union[List, Tuple],
        semitones: int = 0
) -> list:
    """
    Transposes a row (as a list of pitch classes) by an interval of size
    set by the value of 'semitones'.
    """
    zeroList = []
    for x in range(len(row)):
        zeroList.append((row[x] + semitones) % 12)
    return zeroList


def transposeTo(
        row: Union[List, Tuple],
        start: int = 0
) -> list:
    """
    Transposes a row (as a list of pitch classes) to start on 0 (by default), or
    any another number from 0-12 set by the value of 'start'.
    """
    firstPC = row[0]
    zeroList = []
    for y in range(len(row)):
        zeroList.append((row[y] - firstPC + start) % 12)
    return zeroList


def retrograde(
        row: Union[List, Tuple]
) -> list:
    """
    Retrograde a row (simply reverse the pitch list).
    """
    return row[::-1]


def invert(
        row: Union[List, Tuple]
) -> list:
    """
    Invert a row around its starting pitch.
    """
    startingPitch = row[0]
    return [(startingPitch - x) % 12 for x in row]


# ------------------------------------------------------------------------------

def pitchesToIntervals(
        row: Union[List, Tuple],
        wrap: bool = False
) -> list:
    """
    Retrieve the interval succession of a row (mod 12) from a row (list of pitch classes).

    By default (wrap = False) this function returns 11 intervals for a 12 tone row.
    Setting wrap to True gives the '12th' interval: that between the last and the first pitch.
    """
    intervals = []
    if wrap:
        row += row[0]
    for i in range(1, len(row)):
        intervals.append((row[i] - row[i - 1]) % 12)
    return intervals


# ------------------------------------------------------------------------------

# Rotations and swaps including some more niche operations from Krenek 1960

def rotate(
        row: Union[List, Tuple],
        steps: int = 1
) -> list:
    """
    Rotates a row through N steps (i.e. starts on the Nth element).

    Should be called on an integer < 12.
    If called on a larger integer, the value modulo 12 will be taken
    (e.g. 15 becomes 3).
    """
    if steps > 12:
        steps = steps % 12

    return row[steps:] + row[:steps]


def rotateHexachords(
        row: Union[List, Tuple],
        transposeIterations: bool = False
) -> list:
    """
    Implements a set of hexachord rotations of the kind described in Krenek 1960, p.212.
    Splits the row into two hexachords and iteratively rotates each.
    This function returns a list of lists with each iteration until
    the cycle is complete and come full circle.

    The transposeIterations option (default False) transposes each iteration to
    start on the original pitch of the hexachord, also as described by Krenek.
    Note this often converts a 12-tone row into one with repeated pitches.
    """

    rows = [row]

    hexachord1note1 = row[0]
    hexachord2note1 = row[6]

    for i in range(1, 6):
        firstHexachord = row[i:6] + row[0:i]
        secondHexachord = row[6+i:] + row[6:6+i]

        if transposeIterations:
            firstHexachord = transposeTo(firstHexachord, start=hexachord1note1)
            secondHexachord = transposeTo(secondHexachord, start=hexachord2note1)

        newRow = firstHexachord + secondHexachord
        rows.append(newRow)

    rows.append(row)  # completes the cycle

    return rows


def pairSwapKrenek(
        row: Union[List, Tuple]
) -> list:
    """
    Iteratively swaps pairs of adjacent notes in a row
    with a two-step process as described in Krenek 1960, p.213.

    Returns a list of 13 rows of which the last is the retrograde of the first.
    As such, calling this twice brings you back to the original row.
    """

    rows = [row]

    for pair in range(6):

        # First swap type, starting at position 1 (2nd pitch)
        row = [x for x in row]
        for x in range(1, 11, 2):
            row[x], row[x + 1] = row[x + 1], row[x]
        rows.append(row)

        # Second swap type, starting at position 0 (1st pitch)
        row = [x for x in row]
        for x in range(0, 12, 2):
            row[x], row[x + 1] = row[x + 1], row[x]
        rows.append(row)

    return rows


# ------------------------------------------------------------------------------

class RowTester(unittest.TestCase):

    def testTranspose(self):
        rowBoulez = [3, 2, 9, 8, 7, 6, 4, 1, 0, 10, 5, 11]
        zeroBoulez = transposeTo(rowBoulez, start=0)
        self.assertEqual(zeroBoulez, [0, 11, 6, 5, 4, 3, 1, 10, 9, 7, 2, 8])
        transBoulez = transposeTo(zeroBoulez, start=3)
        self.assertEqual(transBoulez, [3, 2, 9, 8, 7, 6, 4, 1, 0, 10, 5, 11])
        byByBoulez = transposeBy(transBoulez, semitones=2)
        self.assertEqual(byByBoulez, [5, 4, 11, 10, 9, 8, 6, 3, 2, 0, 7, 1])

    def testRotate(self):
        luto = [0, 6, 5, 11, 10, 4, 3, 9, 8, 2, 1, 7]
        for i in range(12):
            row = rotate(luto, i)
            self.assertEqual(row[0], luto[i])

    def testInvert(self):
        testSet = [0, 1, 4, 6]
        self.assertEqual(invert(testSet), [0, 11, 8, 6])

    def testPitchesToIntervals(self):
        testRowUp = [x for x in range(12)]
        self.assertEqual(pitchesToIntervals(testRowUp), [1]*11)
        testRowDown = testRowUp[::-1]
        self.assertEqual(pitchesToIntervals(testRowDown), [11]*11)

    def testRotateHexachords(self):
        """Using Krenek's example"""
        rowKrenek = [5, 7, 9, 10, 1, 3, 11, 0, 2, 4, 6, 8]
        rotatedKrenek = rotateHexachords(rowKrenek)
        self.assertEqual(len(rotatedKrenek), 7)
        self.assertEqual(rotatedKrenek[-1], rowKrenek)

    def testPairSwapAndRetrograde(self):
        """Using Krenek's example"""
        testRow = [9, 2, 3, 6, 5, 1, 7, 4, 8, 0, 10, 11]
        testPairSwapKrenek = pairSwapKrenek(testRow)
        self.assertEqual(len(testPairSwapKrenek), 13)
        self.assertEqual(testPairSwapKrenek[-1], retrograde(testRow))


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
