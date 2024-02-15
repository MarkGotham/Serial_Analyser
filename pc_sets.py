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

Properties of pitch class sets, and
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

For more information on set classes and a more detailed list of properties, see
Robert Morris's table and brief explanation (with further sources) here:
http://ecmc.rochester.edu/rdm/pdflib/set-class.table.pdf
"""

from typing import Union, List, Tuple
import transformations
import unittest

# ------------------------------------------------------------------------------

# PC set properties
setClassesList = (

    (  # Cardinality 0 not supported
        None
    ),

    (  # Cardinality 1 not supported
        None
    ),

    (  # Cardinality 2
        ('2-1', (0, 1), (1, 0, 0, 0, 0, 0), 2),
        ('2-2', (0, 2), (0, 1, 0, 0, 0, 0), 2),
        ('2-3', (0, 3), (0, 0, 1, 0, 0, 0), 2),
        ('2-4', (0, 4), (0, 0, 0, 1, 0, 0), 2),
        ('2-5', (0, 5), (0, 0, 0, 0, 1, 0), 2),
        ('2-6', (0, 6), (0, 0, 0, 0, 0, 1), 6)
    ),

    (  # Cardinality 3
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
        ('3-12', (0, 4, 8), (0, 0, 0, 3, 0, 0), 4)
    ),

    (  # Cardinality 4
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
        ('4-Z29', (0, 1, 3, 7), (1, 1, 1, 1, 1, 1), 24)
    ),

    (  # Cardinality 5
        ('5-1', (0, 1, 2, 3, 4), (4, 3, 2, 1, 0, 0), 12),
        ('5-2', (0, 1, 2, 3, 5), (3, 3, 2, 1, 1, 0), 24),
        ('5-3', (0, 1, 2, 4, 5), (3, 2, 2, 2, 1, 0), 24),
        ('5-4', (0, 1, 2, 3, 6), (3, 2, 2, 1, 1, 1), 24),
        ('5-5', (0, 1, 2, 3, 7), (3, 2, 1, 1, 2, 1), 24),
        ('5-6', (0, 1, 2, 5, 6), (3, 1, 1, 2, 2, 1), 24),
        ('5-7', (0, 1, 2, 6, 7), (3, 1, 0, 1, 3, 2), 24),
        ('5-8', (0, 2, 3, 4, 6), (2, 3, 2, 2, 0, 1), 12),
        ('5-9', (0, 1, 2, 4, 6), (2, 3, 1, 2, 1, 1), 24),
        ('5-10', (0, 1, 3, 4, 6), (2, 2, 3, 1, 1, 1), 24),
        ('5-11', (0, 2, 3, 4, 7), (2, 2, 2, 2, 2, 0), 24),
        ('5-12', (0, 1, 3, 5, 6), (2, 2, 2, 1, 2, 1), 12),
        ('5-13', (0, 1, 2, 4, 8), (2, 2, 1, 3, 1, 1), 24),
        ('5-14', (0, 1, 2, 5, 7), (2, 2, 1, 1, 3, 1), 24),
        ('5-15', (0, 1, 2, 6, 8), (2, 2, 0, 2, 2, 2), 12),
        ('5-16', (0, 1, 3, 4, 7), (2, 1, 3, 2, 1, 1), 24),
        ('5-17', (0, 1, 3, 4, 8), (2, 1, 2, 3, 2, 0), 12),
        ('5-18', (0, 1, 4, 5, 7), (2, 1, 2, 2, 2, 1), 24),
        ('5-19', (0, 1, 3, 6, 7), (2, 1, 2, 1, 2, 2), 24),
        ('5-20', (0, 1, 3, 7, 8), (2, 1, 1, 2, 3, 1), 24),
        ('5-21', (0, 1, 4, 5, 8), (2, 0, 2, 4, 2, 0), 24),
        ('5-22', (0, 1, 4, 7, 8), (2, 0, 2, 3, 2, 1), 12),
        ('5-23', (0, 2, 3, 5, 7), (1, 3, 2, 1, 3, 0), 24),
        ('5-24', (0, 1, 3, 5, 7), (1, 3, 1, 2, 2, 1), 24),
        ('5-25', (0, 2, 3, 5, 8), (1, 2, 3, 1, 2, 1), 24),
        ('5-26', (0, 2, 4, 5, 8), (1, 2, 2, 3, 1, 1), 24),
        ('5-27', (0, 1, 3, 5, 8), (1, 2, 2, 2, 3, 0), 24),
        ('5-28', (0, 2, 3, 6, 8), (1, 2, 2, 2, 1, 2), 24),
        ('5-29', (0, 1, 3, 6, 8), (1, 2, 2, 1, 3, 1), 24),
        ('5-30', (0, 1, 4, 6, 8), (1, 2, 1, 3, 2, 1), 24),
        ('5-31', (0, 1, 3, 6, 9), (1, 1, 4, 1, 1, 2), 24),
        ('5-32', (0, 1, 4, 6, 9), (1, 1, 3, 2, 2, 1), 24),
        ('5-33', (0, 2, 4, 6, 8), (0, 4, 0, 4, 0, 2), 12),
        ('5-34', (0, 2, 4, 6, 9), (0, 3, 2, 2, 2, 1), 12),
        ('5-35', (0, 2, 4, 7, 9), (0, 3, 2, 1, 4, 0), 12),
        ('5-36', (0, 1, 2, 4, 7), (2, 2, 2, 1, 2, 1), 24),
        ('5-37', (0, 3, 4, 5, 8), (2, 1, 2, 3, 2, 0), 12),
        ('5-38', (0, 1, 2, 5, 8), (2, 1, 2, 2, 2, 1), 24)
    ),

    (  # Cardinality 6
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
        ('6-Z50', (0, 1, 4, 6, 7, 9), (2, 2, 4, 2, 3, 2), 12, 'RI')
    ),

    (  # Cardinality 7
        ('7-1', (0, 1, 2, 3, 4, 5, 6), (6, 5, 4, 3, 2, 1), 12),
        ('7-2', (0, 1, 2, 3, 4, 5, 7), (5, 5, 4, 3, 3, 1), 24),
        ('7-3', (0, 1, 2, 3, 4, 5, 8), (5, 4, 4, 4, 3, 1), 24),
        ('7-4', (0, 1, 2, 3, 4, 6, 7), (5, 4, 4, 3, 3, 2), 24),
        ('7-5', (0, 1, 2, 3, 5, 6, 7), (5, 4, 3, 3, 4, 2), 24),
        ('7-6', (0, 1, 2, 3, 4, 7, 8), (5, 3, 3, 4, 4, 2), 24),
        ('7-7', (0, 1, 2, 3, 6, 7, 8), (5, 3, 2, 3, 5, 3), 24),
        ('7-8', (0, 2, 3, 4, 5, 6, 8), (4, 5, 4, 4, 2, 2), 12),
        ('7-9', (0, 1, 2, 3, 4, 6, 8), (4, 5, 3, 4, 3, 2), 24),
        ('7-10', (0, 1, 2, 3, 4, 6, 9), (4, 4, 5, 3, 3, 2), 24),
        ('7-11', (0, 1, 3, 4, 5, 6, 8), (4, 4, 4, 4, 4, 1), 24),
        ('7-Z12', (0, 1, 2, 3, 4, 7, 9), (4, 4, 4, 3, 4, 2), 12),
        ('7-13', (0, 1, 2, 4, 5, 6, 8), (4, 4, 3, 5, 3, 2), 24),
        ('7-14', (0, 1, 2, 3, 5, 7, 8), (4, 4, 3, 3, 5, 2), 24),
        ('7-15', (0, 1, 2, 4, 6, 7, 8), (4, 4, 2, 4, 4, 3), 12),
        ('7-16', (0, 1, 2, 3, 5, 6, 9), (4, 3, 5, 4, 3, 2), 24),
        ('7-Z17', (0, 1, 2, 4, 5, 6, 9), (4, 3, 4, 5, 4, 1), 12),
        ('7-Z18', (0, 1, 2, 3, 5, 8, 9), (4, 3, 4, 4, 4, 2), 24),
        ('7-19', (0, 1, 2, 3, 6, 7, 9), (4, 3, 4, 3, 4, 3), 24),
        ('7-20', (0, 1, 2, 4, 7, 8, 9), (4, 3, 3, 4, 5, 2), 24),
        ('7-21', (0, 1, 2, 4, 5, 8, 9), (4, 2, 4, 6, 4, 1), 24),
        ('7-22', (0, 1, 2, 5, 6, 8, 9), (4, 2, 4, 5, 4, 2), 12),
        ('7-23', (0, 2, 3, 4, 5, 7, 9), (3, 5, 4, 3, 5, 1), 24),
        ('7-24', (0, 1, 2, 3, 5, 7, 9), (3, 5, 3, 4, 4, 2), 24),
        ('7-25', (0, 2, 3, 4, 6, 7, 9), (3, 4, 5, 3, 4, 2), 24),
        ('7-26', (0, 1, 3, 4, 5, 7, 9), (3, 4, 4, 5, 3, 2), 24),
        ('7-27', (0, 1, 2, 4, 5, 7, 9), (3, 4, 4, 4, 5, 1), 24),
        ('7-28', (0, 1, 3, 5, 6, 7, 9), (3, 4, 4, 4, 3, 3), 24),
        ('7-29', (0, 1, 2, 4, 6, 7, 9), (3, 4, 4, 3, 5, 2), 24),
        ('7-30', (0, 1, 2, 4, 6, 8, 9), (3, 4, 3, 5, 4, 2), 24),
        ('7-31', (0, 1, 3, 4, 6, 7, 9), (3, 3, 6, 3, 3, 3), 24),
        ('7-32', (0, 1, 3, 4, 6, 8, 9), (3, 3, 5, 4, 4, 2), 24),
        ('7-33', (0, 1, 2, 4, 6, 8, 10), (2, 6, 2, 6, 2, 3), 12),
        ('7-34', (0, 1, 3, 4, 6, 8, 10), (2, 5, 4, 4, 4, 2), 12),
        ('7-35', (0, 1, 3, 5, 6, 8, 10), (2, 5, 4, 3, 6, 1), 12),
        ('7-Z36', (0, 1, 2, 3, 5, 6, 8), (4, 4, 4, 3, 4, 2), 24),
        ('7-Z37', (0, 1, 3, 4, 5, 7, 8), (4, 3, 4, 5, 4, 1), 12),
        ('7-Z38', (0, 1, 2, 4, 5, 7, 8), (4, 3, 4, 4, 4, 2), 24)
    ),

    (  # Cardinality 8
        ('8-1', (0, 1, 2, 3, 4, 5, 6, 7), (7, 6, 5, 4, 4, 2), 12),
        ('8-2', (0, 1, 2, 3, 4, 5, 6, 8), (6, 6, 5, 5, 4, 2), 24),
        ('8-3', (0, 1, 2, 3, 4, 5, 6, 9), (6, 5, 6, 5, 4, 2), 12),
        ('8-4', (0, 1, 2, 3, 4, 5, 7, 8), (6, 5, 5, 5, 5, 2), 24),
        ('8-5', (0, 1, 2, 3, 4, 6, 7, 8), (6, 5, 4, 5, 5, 3), 24),
        ('8-6', (0, 1, 2, 3, 5, 6, 7, 8), (6, 5, 4, 4, 6, 3), 12),
        ('8-7', (0, 1, 2, 3, 4, 5, 8, 9), (6, 4, 5, 6, 5, 2), 12),
        ('8-8', (0, 1, 2, 3, 4, 7, 8, 9), (6, 4, 4, 5, 6, 3), 12),
        ('8-9', (0, 1, 2, 3, 6, 7, 8, 9), (6, 4, 4, 4, 6, 4), 6),
        ('8-10', (0, 2, 3, 4, 5, 6, 7, 9), (5, 6, 6, 4, 5, 2), 12),
        ('8-11', (0, 1, 2, 3, 4, 5, 7, 9), (5, 6, 5, 5, 5, 2), 24),
        ('8-12', (0, 1, 3, 4, 5, 6, 7, 9), (5, 5, 6, 5, 4, 3), 24),
        ('8-13', (0, 1, 2, 3, 4, 6, 7, 9), (5, 5, 6, 4, 5, 3), 24),
        ('8-14', (0, 1, 2, 4, 5, 6, 7, 9), (5, 5, 5, 5, 6, 2), 24),
        ('8-Z15', (0, 1, 2, 3, 4, 6, 8, 9), (5, 5, 5, 5, 5, 3), 24),
        ('8-16', (0, 1, 2, 3, 5, 7, 8, 9), (5, 5, 4, 5, 6, 3), 24),
        ('8-17', (0, 1, 3, 4, 5, 6, 8, 9), (5, 4, 6, 6, 5, 2), 12),
        ('8-18', (0, 1, 2, 3, 5, 6, 8, 9), (5, 4, 6, 5, 5, 3), 24),
        ('8-19', (0, 1, 2, 4, 5, 6, 8, 9), (5, 4, 5, 7, 5, 2), 24),
        ('8-20', (0, 1, 2, 4, 5, 7, 8, 9), (5, 4, 5, 6, 6, 2), 12),
        ('8-21', (0, 1, 2, 3, 4, 6, 8, 10), (4, 7, 4, 6, 4, 3), 12),
        ('8-22', (0, 1, 2, 3, 5, 6, 8, 10), (4, 6, 5, 5, 6, 2), 24),
        ('8-23', (0, 1, 2, 3, 5, 7, 8, 10), (4, 6, 5, 4, 7, 2), 12),
        ('8-24', (0, 1, 2, 4, 5, 6, 8, 10), (4, 6, 4, 7, 4, 3), 12),
        ('8-25', (0, 1, 2, 4, 6, 7, 8, 10), (4, 6, 4, 6, 4, 4), 6),
        ('8-26', (0, 1, 2, 4, 5, 7, 9, 10), (4, 5, 6, 5, 6, 2), 12),
        ('8-27', (0, 1, 2, 4, 5, 7, 8, 10), (4, 5, 6, 5, 5, 3), 24),
        ('8-28', (0, 1, 3, 4, 6, 7, 9, 10), (4, 4, 8, 4, 4, 4), 3),
        ('8-Z29', (0, 1, 2, 3, 5, 6, 7, 9), (5, 5, 5, 5, 5, 3), 24)
    ),

    (  # Cardinality 9
        ('9-1', (0, 1, 2, 3, 4, 5, 6, 7, 8), (8, 7, 6, 6, 6, 3), 12),
        ('9-2', (0, 1, 2, 3, 4, 5, 6, 7, 9), (7, 7, 7, 6, 6, 3), 24),
        ('9-3', (0, 1, 2, 3, 4, 5, 6, 8, 9), (7, 6, 7, 7, 6, 3), 24),
        ('9-4', (0, 1, 2, 3, 4, 5, 7, 8, 9), (7, 6, 6, 7, 7, 3), 24),
        ('9-5', (0, 1, 2, 3, 4, 6, 7, 8, 9), (7, 6, 6, 6, 7, 4), 24),
        ('9-6', (0, 1, 2, 3, 4, 5, 6, 8, 10), (6, 8, 6, 7, 6, 3), 12),
        ('9-7', (0, 1, 2, 3, 4, 5, 7, 8, 10), (6, 7, 7, 6, 7, 3), 24),
        ('9-8', (0, 1, 2, 3, 4, 6, 7, 8, 10), (6, 7, 6, 7, 6, 4), 24),
        ('9-9', (0, 1, 2, 3, 5, 6, 7, 8, 10), (6, 7, 6, 6, 8, 3), 12),
        ('9-10', (0, 1, 2, 3, 4, 6, 7, 9, 10), (6, 6, 8, 6, 6, 4), 12),
        ('9-11', (0, 1, 2, 3, 5, 6, 7, 9, 10), (6, 6, 7, 7, 7, 3), 24),
        ('9-12', (0, 1, 2, 4, 5, 6, 8, 9, 10), (6, 6, 6, 9, 6, 3), 4)
    ),

    (  # Cardinality 10
        ('10-1', (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (9, 8, 8, 8, 8, 4), 12),
        ('10-2', (0, 1, 2, 3, 4, 5, 6, 7, 8, 10), (8, 9, 8, 8, 8, 4), 12),
        ('10-3', (0, 1, 2, 3, 4, 5, 6, 7, 9, 10), (8, 8, 9, 8, 8, 4), 12),
        ('10-4', (0, 1, 2, 3, 4, 5, 6, 8, 9, 10), (8, 8, 8, 9, 8, 4), 12),
        ('10-5', (0, 1, 2, 3, 4, 5, 7, 8, 9, 10), (8, 8, 8, 8, 9, 4), 12),
        ('10-6', (0, 1, 2, 3, 4, 6, 7, 8, 9, 10), (8, 8, 8, 8, 8, 5), 6)
    ),

    (  # Cardinality 11 not supported
        None
    ),

    (  # Cardinality 12 not supported
        None
    )

)


def setClassesFromCardinality(cardinality: int):
    """
    In: a cardinality (2-10).
    Out: the pitch class set data for that cardinality.
    """
    if not (1 < cardinality < 11):
        raise ValueError('Invalid cardinality: must be 2-10 (inclusive).')
    else:
        return setClassesList[cardinality]


def primeToCombinatoriality(prime: Tuple[int]):
    """
    In: a prime form expressed as a Tuple of integers.
    Out: the combinatoriality status as a string.
    """
    data = setClassesFromCardinality(len(prime))
    for x in data:
        if x[1] == prime:
            return x[3]
    raise ValueError(f'{prime} is not a valid prime form')


def intervalVectorToCombinatoriality(vector: Tuple[int]):
    """
    In: an interval vector for any set with 2-10 distinct pitches,
    expressed as a Tuple of 6 integers.
    Out: the combinatoriality status of any valid interval vector as a
    string (one of T, I, RI, A, or an empty string for non-combinatorial cases).
    """
    if len(vector) != 6:
        raise ValueError(f'{vector} is not a valid interval vector')
    total = sum(vector)
    totalToCardinality = {1: 2,
                          3: 3,
                          6: 4,
                          15: 6}
    data = setClassesFromCardinality(totalToCardinality[total])
    for x in data:
        if x[2] == vector:
            return x[-1]
    raise ValueError(f'{vector} is not a valid interval vector')


def pitchesToCombinatoriality(pitches: Union[List[int], Tuple[int]]):
    """
    In: a list or tuple of pitches expressed as integers (0–11) for sets with 2-10 distinct pitches.
    Out: the combinatoriality status as a string.
    """
    icv = pitchesToIntervalVector(pitches)
    return intervalVectorToCombinatoriality(icv)


def distinctPCs(pitches: Union[List, Tuple]) -> list:
    """
    In: a list or tuple of pitches (any integers).
    Out: a list of distinct PCs in the range 0-11.
    """
    pitches = list(set(pitches))  # remove any duplicates
    return [p % 12 for p in pitches]


def pitchesToIntervalVector(pitches: Union[List[int], Tuple[int]]):
    """
    In: a list or tuple of pitches.
    Out: the interval vector.
    """
    pitches = distinctPCs(pitches)

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


def pitchesToForteClass(pitches: Union[List[int], Tuple[int]]):
    """
    In: a list or tuple of pitches expressed as integers (0–11) for sets with 2-10 distinct pitches.
    Out: the Forte class.
    """
    data = setClassesFromCardinality(len(pitches))
    prime = pitchesToPrime(pitches)
    for x in data:
        if x[1] == prime:
            return x[0]
    raise ValueError(f'{pitches} is not a valid entry.')


def pitchesToPrime(pitches: Union[List[int], Tuple[int]]):
    """
    In: a list or tuple of pitches expressed as integers (0–11) for sets with 2-10 distinct pitches.
    Out: the prime form.

    The function first converts the pitches to their interval vector (easy, fast).
    That vector unambiguously gives the prime form for cases except those with Z-related pairs.
    This affects one pair of tetrachords (so 2 prime forms) and 15 pairs of hexachords (30 primes).

    In those cases, the prime form is worked out by comparing the pitch list against the pair of
    options in both inversions until a match is found.
    """

    pitches = distinctPCs(pitches)

    vector = pitchesToIntervalVector(pitches)
    primes = []
    data = setClassesFromCardinality(len(set(pitches)))

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

        # Test one case of numbers beyond 0-11
        prime = pitchesToPrime((100, 102, 103))
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
        for entry in setClassesFromCardinality(6):
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

