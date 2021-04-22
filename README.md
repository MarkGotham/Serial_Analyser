# Serial_Analyser
Functions for working with 12-tone serial music (work in progress)

## [Row Analyser](./row_analyser.py)

Functions for investigating the properties of tone rows, centered on:
- sub-segments (overlapping or discrete) for derived rows, and
- combinatoriality properties

## [Transformations](./transformations.py)

Routine serial functions for transforming pitch like tone rows:
- transposition, 
- inversion, 
- retrograde, 
- rotation,

in any combination (e.g. transposed retrograde inversion), 
along with a couple of more niche operations.

## [PC Sets](./pc_sets.py)

Supporting data setting out the properties of 
pc sets with cardinality 2, 3, 4, and 6 
(dyads, trichords, tetrachords, and hexachords)
along with functions for retrieving one such property directly from another, 
or directly from any list of pitch classes 
(e.g. `pitchesToIntervalVector`).

Each pitch class set entry features at least the following properties:
- Forte index;
- prime form (according to Forte's system);
- interval vector;
- number of distinct transformations (non-invariant transpositions and / or inversions).

## Coming soon

A substantial list of rows used in the repertoire,
set out both 'neutrally' and 
anthologized according to row properties. 
