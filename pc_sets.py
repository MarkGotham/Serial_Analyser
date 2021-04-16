"""
===============================
PC Sets (pc_sets.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Properties of trichords, tetrachords, and hexachords, along with
functions for retrieving one property directly from another.

Each pitch class set entry features the following properties:
- Forte index;
- prime form (according to Forte's system);
- interval vector;
- number of distinct transformations (non-invariant transpositions and / or inversions).

For the hexachords (only), an additional entry provides the combinatoriality status
from among 5 options:
'A' for all-combinatorial (6 hexachords total),
'T' for transposition only (only 1),
'I' for inversion only (13),
'RI' for retrograde-inversion only (13), and
'' (an empty string) for non-combinatorial (16).

Most of the retrieval function names are in the form
`<call-on-type>To<return-type>`
e.g.
`primeToCombinatoriality`
Some are simple mappings from one entry to another.
Anything starting with pitches involves more calculation.

"""

from typing import Union, List, Tuple
import transformations
import unittest

# ------------------------------------------------------------------------------

# PC set properties
dyads = (
    ('2-1', (0, 1), (1, 0, 0, 0, 0, 0), 2),
    ('2-2', (0, 2), (0, 1, 0, 0, 0, 0), 2),
    ('2-3', (0, 3), (0, 0, 1, 0, 0, 0), 2),
    ('2-4', (0, 4), (0, 0, 0, 1, 0, 0), 2),
    ('2-5', (0, 5), (0, 0, 0, 0, 1, 0), 2),
    ('2-6', (0, 6), (0, 0, 0, 0, 0, 1), 6))

trichords = (
    ('3-1', (0, 1, 2), (2, 1, 0, 0, 0, 0), 12),
    ('3-2', (0, 1, 3), (1, 1, 1, 0, 0, 0), 24),
    ('3-3', (0, 1, 4), (1, 0, 1, 1, 0, 0), 24),
    ('3-4', (0, 1, 5), (1, 0, 0, 1, 1, 0), 24),
    ('3-5', (0, 1, 6), (1, 0, 0, 0, 1, 1), 24),
    ('3-6', (0, 2, 4), (0, 2, 0, 1, 0, 0), 12),
    ('3-7', (0, 2, 5), (0, 1, 1, 0, 1, 0), 24),
    ('3-8', (0, 2, 6), (0, 1, 0, 1, 0, 1), 24),
    ('3-9', (0, 2, 7), (0, 1, 0, 0, 2, 0), 12),
    ('3-10', (0, 3, 6), (0, 0, 2, 0, 0, 1), 12),
    ('3-11', (0, 3, 7), (0, 0, 1, 1, 1, 0), 24),
    ('3-12', (0, 4, 8), (0, 0, 0, 3, 0, 0), 4))

tetrachords = (
    ('4-1', (0, 1, 2, 3), (3, 2, 1, 0, 0, 0), 12),
    ('4-2', (0, 1, 2, 4), (2, 2, 1, 1, 0, 0), 24),
    ('4-3', (0, 1, 3, 4), (2, 1, 2, 1, 0, 0), 12),
    ('4-4', (0, 1, 2, 5), (2, 1, 1, 1, 1, 0), 24),
    ('4-5', (0, 1, 2, 6), (2, 1, 0, 1, 1, 1), 24),
    ('4-6', (0, 1, 2, 7), (2, 1, 0, 0, 2, 1), 12),
    ('4-7', (0, 1, 4, 5), (2, 0, 1, 2, 1, 0), 12),
    ('4-8', (0, 1, 5, 6), (2, 0, 0, 1, 2, 1), 12),
    ('4-9', (0, 1, 6, 7), (2, 0, 0, 0, 2, 2), 6),
    ('4-10', (0, 2, 3, 5), (1, 2, 2, 0, 1, 0), 12),
    ('4-11', (0, 1, 3, 5), (1, 2, 1, 1, 1, 0), 24),
    ('4-12', (0, 2, 3, 6), (1, 1, 2, 1, 0, 1), 24),
    ('4-13', (0, 1, 3, 6), (1, 1, 2, 0, 1, 1), 24),
    ('4-14', (0, 2, 3, 7), (1, 1, 1, 1, 2, 0), 24),
    ('4-Z15', (0, 1, 4, 6), (1, 1, 1, 1, 1, 1), 24),
    ('4-16', (0, 1, 5, 7), (1, 1, 0, 1, 2, 1), 24),
    ('4-17', (0, 3, 4, 7), (1, 0, 2, 2, 1, 0), 12),
    ('4-18', (0, 1, 4, 7), (1, 0, 2, 1, 1, 1), 24),
    ('4-19', (0, 1, 4, 8), (1, 0, 1, 3, 1, 0), 24),
    ('4-20', (0, 1, 5, 8), (1, 0, 1, 2, 2, 0), 12),
    ('4-21', (0, 2, 4, 6), (0, 3, 0, 2, 0, 1), 12),
    ('4-22', (0, 2, 4, 7), (0, 2, 1, 1, 2, 0), 24),
    ('4-23', (0, 2, 5, 7), (0, 2, 1, 0, 3, 0), 12),
    ('4-24', (0, 2, 4, 8), (0, 2, 0, 3, 0, 1), 12),
    ('4-25', (0, 2, 6, 8), (0, 2, 0, 2, 0, 2), 6),
    ('4-26', (0, 3, 5, 8), (0, 1, 2, 1, 2, 0), 12),
    ('4-27', (0, 2, 5, 8), (0, 1, 2, 1, 1, 1), 24),
    ('4-28', (0, 3, 6, 9), (0, 0, 4, 0, 0, 2), 3),
    ('4-Z29', (0, 1, 3, 7), (1, 1, 1, 1, 1, 1), 24))

hexachords = (
    ('6-1', (0, 1, 2, 3, 4, 5), (5, 4, 3, 2, 1, 0), 12, 'A'),
    ('6-2', (0, 1, 2, 3, 4, 6), (4, 4, 3, 2, 1, 1), 24, 'I'),
    ('6-Z3', (0, 1, 2, 3, 5, 6), (4, 3, 3, 2, 2, 1), 24, ''),
    ('6-Z4', (0, 1, 2, 4, 5, 6), (4, 3, 2, 3, 2, 1), 12, 'RI'),
    ('6-5', (0, 1, 2, 3, 6, 7), (4, 2, 2, 2, 3, 2), 24, 'I'),
    ('6-Z6', (0, 1, 2, 5, 6, 7), (4, 2, 1, 2, 4, 2), 12, 'RI'),
    ('6-7', (0, 1, 2, 6, 7, 8), (4, 2, 0, 2, 4, 3), 6, 'A'),
    ('6-8', (0, 2, 3, 4, 5, 7), (3, 4, 3, 2, 3, 0), 12, 'A'),
    ('6-9', (0, 1, 2, 3, 5, 7), (3, 4, 2, 2, 3, 1), 24, 'I'),
    ('6-Z10', (0, 1, 3, 4, 5, 7), (3, 3, 3, 3, 2, 1), 24, ''),
    ('6-Z11', (0, 1, 2, 4, 5, 7), (3, 3, 3, 2, 3, 1), 24, ''),
    ('6-Z12', (0, 1, 2, 4, 6, 7), (3, 3, 2, 2, 3, 2), 24, ''),
    ('6-Z13', (0, 1, 3, 4, 6, 7), (3, 2, 4, 2, 2, 2), 12, 'RI'),
    ('6-14', (0, 1, 3, 4, 5, 8), (3, 2, 3, 4, 3, 0), 24, 'T'),
    ('6-15', (0, 1, 2, 4, 5, 8), (3, 2, 3, 4, 2, 1), 24, 'I'),
    ('6-16', (0, 1, 4, 5, 6, 8), (3, 2, 2, 4, 3, 1), 24, 'I'),
    ('6-Z17', (0, 1, 2, 4, 7, 8), (3, 2, 2, 3, 3, 2), 24, ''),
    ('6-18', (0, 1, 2, 5, 7, 8), (3, 2, 2, 2, 4, 2), 24, 'I'),
    ('6-Z19', (0, 1, 3, 4, 7, 8), (3, 1, 3, 4, 3, 1), 24, ''),
    ('6-20', (0, 1, 4, 5, 8, 9), (3, 0, 3, 6, 3, 0), 4, 'A'),
    ('6-21', (0, 2, 3, 4, 6, 8), (2, 4, 2, 4, 1, 2), 24, 'I'),
    ('6-22', (0, 1, 2, 4, 6, 8), (2, 4, 1, 4, 2, 2), 24, 'I'),
    ('6-Z23', (0, 2, 3, 5, 6, 8), (2, 3, 4, 2, 2, 2), 12, 'RI'),
    ('6-Z24', (0, 1, 3, 4, 6, 8), (2, 3, 3, 3, 3, 1), 24, ''),
    ('6-Z25', (0, 1, 3, 5, 6, 8), (2, 3, 3, 2, 4, 1), 24, ''),
    ('6-Z26', (0, 1, 3, 5, 7, 8), (2, 3, 2, 3, 4, 1), 12, 'RI'),
    ('6-27', (0, 1, 3, 4, 6, 9), (2, 2, 5, 2, 2, 2), 24, 'I'),
    ('6-Z28', (0, 1, 3, 5, 6, 9), (2, 2, 4, 3, 2, 2), 12, 'RI'),
    ('6-Z29', (0, 1, 3, 6, 8, 9), (2, 2, 4, 2, 3, 2), 12, 'RI'),
    ('6-30', (0, 1, 3, 6, 7, 9), (2, 2, 4, 2, 2, 3), 12, 'I'),
    ('6-31', (0, 1, 3, 5, 8, 9), (2, 2, 3, 4, 3, 1), 24, 'I'),
    ('6-32', (0, 2, 4, 5, 7, 9), (1, 4, 3, 2, 5, 0), 12, 'A'),
    ('6-33', (0, 2, 3, 5, 7, 9), (1, 4, 3, 2, 4, 1), 24, 'I'),
    ('6-34', (0, 1, 3, 5, 7, 9), (1, 4, 2, 4, 2, 2), 24, 'I'),
    ('6-35', (0, 2, 4, 6, 8, 10), (0, 6, 0, 6, 0, 3), 2, 'A'),
    ('6-Z36', (0, 1, 2, 3, 4, 7), (4, 3, 3, 2, 2, 1), 24, ''),
    ('6-Z37', (0, 1, 2, 3, 4, 8), (4, 3, 2, 3, 2, 1), 12, 'RI'),
    ('6-Z38', (0, 1, 2, 3, 7, 8), (4, 2, 1, 2, 4, 2), 12, 'RI'),
    ('6-Z39', (0, 2, 3, 4, 5, 8), (3, 3, 3, 3, 2, 1), 24, ''),
    ('6-Z40', (0, 1, 2, 3, 5, 8), (3, 3, 3, 2, 3, 1), 24, ''),
    ('6-Z41', (0, 1, 2, 3, 6, 8), (3, 3, 2, 2, 3, 2), 24, ''),
    ('6-Z42', (0, 1, 2, 3, 6, 9), (3, 2, 4, 2, 2, 2), 12, 'RI'),
    ('6-Z43', (0, 1, 2, 5, 6, 8), (3, 2, 2, 3, 3, 2), 24, ''),
    ('6-Z44', (0, 1, 2, 5, 6, 9), (3, 1, 3, 4, 3, 1), 24, ''),
    ('6-Z45', (0, 2, 3, 4, 6, 9), (2, 3, 4, 2, 2, 2), 12, 'RI'),
    ('6-Z46', (0, 1, 2, 4, 6, 9), (2, 3, 3, 3, 3, 1), 24, ''),
    ('6-Z47', (0, 1, 2, 4, 7, 9), (2, 3, 3, 2, 4, 1), 24, ''),
    ('6-Z48', (0, 1, 2, 5, 7, 9), (2, 3, 2, 3, 4, 1), 12, 'RI'),
    ('6-Z49', (0, 1, 3, 4, 7, 9), (2, 2, 4, 3, 2, 2), 12, 'RI'),
    ('6-Z50', (0, 1, 4, 6, 7, 9), (2, 2, 4, 2, 3, 2), 12, 'RI'))


def relevantData(cardinality: int):
    """
    In: a cardinality (currently limited to 2, 3, 4, 6.)
    Out: the pitch class set data for that cardinality.
    """
    if cardinality == 2:
        return dyads
    elif cardinality == 3:
        return trichords
    elif cardinality == 4:
        return tetrachords
    elif cardinality == 6:
        return hexachords
    else:
        raise ValueError(f'Cardinality {cardinality} not currently supported.')


def primeToCombinatoriality(prime: Tuple[int]):
    """
    In: a prime form expressed as a Tuple of integers.
    Out: the combinatoriality status as a string.
    """
    data = relevantData(len(prime))
    for x in data:
        if x[1] == prime:
            return x[3]
    raise ValueError(f'{prime} is not a valid prime form')


def intervalVectorToCombinatoriality(vector: Tuple[int]):
    """
    In: an interval vector expressed as a Tuple of 6 integers.
    Out: the combinatoriality status of any valid interval vector as a
    string (one of T, I, RI, A, or an empty string for non-combinatorial cases).

    Currently limited to sets of cardinality 6.
    """
    # TODO cardinality 3 and 4
    if len(vector) != 6:
        raise ValueError(f'{vector} is not a valid interval vector')
    total = sum(vector)
    totalToCardinality = {3: 3,
                          6: 4,
                          15: 6}
    data = relevantData(totalToCardinality[total])
    for x in data:
        if x[2] == vector:
            return x[-1]
    raise ValueError(f'{vector} is not a valid interval vector')


def pitchesToCombinatoriality(pitches: Union[List, Tuple]):
    """
    In: a list or tuple of pitches (currently limited to cardinality 3, 4, 6.)
    Out: the combinatoriality status as a string.
    """
    icv = pitchesToIntervalVector(pitches)
    return intervalVectorToCombinatoriality(icv)


def pitchesToIntervalVector(pitches: Union[List, Tuple]):
    """
    In: a list or tuple of pitches (currently limited to cardinality 3, 4, 6.)
    Out: the interval vector.
    """
    for p in pitches:
        if p not in range(12):
            raise ValueError(f'{pitches} must contain only integers from 0-12')

    vector = [0, 0, 0, 0, 0, 0]
    from itertools import combinations
    for p in combinations(pitches, 2):
        ic = p[1] - p[0]
        if ic < 0:
            ic *= -1
        if ic > 6:
            ic = 12 - ic
        vector[ic - 1] += 1
    return tuple(vector)


def pitchesToForteClass(pitches: Union[List, Tuple]):
    """
    In: a list or tuple of pitches (currently limited to cardinality 3, 4, 6.)
    Out: the Forte class.
    """
    data = relevantData(len(pitches))
    prime = pitchesToPrime(pitches)
    for x in data:
        if x[1] == prime:
            return x[0]
    raise ValueError(f'{pitches} is not a valid entry.')


def pitchesToPrime(pitches: Union[List, Tuple]):
    """
    In: a list or tuple of pitches (currently limited to cardinality 3, 4, 6.)
    Out: the prime form.

    The function first converts the pitches to their interval vector (easy, fast).
    That vector unambiguously gives the prime form for cases except those with Z-related pairs.
    This affects one pair of tetrachords (so 2 prime forms) and 15 pairs of hexachords (30 primes).

    In those cases, the prime form is worked out by comparing the pitch list against the pair of
    options in both inversions until a match is found.
    """
    vector = pitchesToIntervalVector(pitches)
    primes = []
    data = relevantData(len(pitches))

    for x in data:
        if x[2] == vector:
            primes.append(x[1])

    if len(primes) == 1:
        return primes[0]
    elif len(primes) > 1:
        for prime in primes:  # each possible prime form
            invertedPrime = transformations.invert(prime)
            for t in [prime, invertedPrime]:
                if transpositionEquivalent(t, pitches):
                    return prime


def transpositionEquivalent(set1, set2):
    """
    Supporting function for determining whether two sets are transposition equivalent
    as part of determining prime forms with `pitchesToPrime`.
    """
    sortedSet2 = sorted(list(set2))
    for i in range(12):
        testCase = sorted(list(transformations.transposeBy(set1, i)))
        if testCase == sortedSet2:
            return True


# ------------------------------------------------------------------------------

class PCTester(unittest.TestCase):

    def testPitchesToPrime(self):
        """
        Tests one case through the interval vector, and another that requires transformation.
        """
        prime = pitchesToPrime((0, 2, 3))
        self.assertEqual(prime, (0, 1, 3))

        prime = pitchesToPrime((8, 2, 4, 7))  # via I [0,2,5,6], t2 [2,4,7,8], and shuffle.
        self.assertEqual(prime, (0, 1, 4, 6))

    def testSelfComplementHexachords(self):
        """
        Tests that all and only the hexachords without a Z-related pair are self-complementary.
        (In so doing, this also tests the pitches-to-prime routine.)
        """

        countHexachords = 0
        countTotal = 0
        for entry in hexachords:
            hexachord = entry[1]
            complement = tuple([x for x in range(12) if x not in hexachord])
            complementPrime = pitchesToPrime(complement)
            if hexachord == complementPrime:
                self.assertFalse('Z' in entry[0])
                countHexachords += 1
                countTotal += entry[3]
            else:
                self.assertTrue('Z' in entry[0])

        self.assertEqual(countHexachords, 20)  # 20/50, so 40%
        self.assertEqual(countTotal, 372)  # 372/924, so 35.4%


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
