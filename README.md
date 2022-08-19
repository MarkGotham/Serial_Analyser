# Serial Analyser
This repo provides 
code for working with 12-tone serial rows
and a corpus of examples from the repertoire.

‘A very useful resource’ — [Professor Robert D. Morris](https://www.esm.rochester.edu/faculty/morris_robert/) 

## Code

### [Row Analyser](./row_analyser.py)

Functions for investigating the properties of tone rows, centered on:
- sub-segments (overlapping or discrete) for derived rows, and
- combinatoriality properties

### [Transformations](./transformations.py)

Routine serial functions for transforming pitch like tone rows:
- transposition, 
- inversion, 
- retrograde, 
- rotation,

in any combination (e.g. transposed retrograde inversion), 
along with a couple of more niche operations.

### [PC Sets](./pc_sets.py)

Supporting data setting out the properties of 
pc sets with cardinality 2-10 
(dyads, trichords, tetrachords, ...)
along with functions for retrieving one such property directly from another, 
or directly from any list of pitch classes 
(e.g. `pitchesToIntervalVector`).

Each pitch class set entry features at least the following properties:
- Forte index;
- prime form (according to Forte's system);
- interval vector;
- number of distinct transformations (non-invariant transpositions and / or inversions).

## Anthology

A substantial list of rows used in the repertoire,
set out both 'neutrally' and 
anthologized according to row properties:
- as a [tabular list](./Repertoire_Anthology/rows_in_the_repertoire.csv) 
- in musical notation: [.mscz](./Repertoire_Anthology/Rows_in_the_Repertoire.mscz), [.mxl](./Repertoire_Anthology/Rows_in_the_Repertoire.mxl)
- as [an html page with rows organised by property](./Repertoire_Anthology/Serial_Anthology.html)

## Links to this material hosted elsewhere

The musical notation is also 
[viewable here](https://musescore.com/fourscoreandmore/rows-in-the-repertoire) 
and embedded in 
[this textbook chapter](https://viva.pressbooks.pub/openmusictheory/chapter/anthology-12-tone/) 
along with the anthology listings.

I report on all of this (code, list, anthology, and more) 
in a joint paper with Jason Yust 
published with [DLfM](https://dlfm.web.ox.ac.uk), 
that is [viewable here](https://doi.org/10.1145/3469013.3469018),
and open access to all when approached from [this table of contents page](https://dlfm.web.ox.ac.uk/2021-proceedings).
.
Please cite that piece in any public-facing use of this work:
```
Gotham, Mark and Jason Yust. 2021. ‘Serial Analysis: A Digital Library of Rows in the
 Repertoire and their Properties, with Applications for Teaching and Research'. In 8th International Conference on Digital Libraries for Musicology (DLfM2021), July 28–30, 2021, Virtual Conference, GA, USA. , Ove Nordwall (Ed.). ACM, New York, NY, USA 9 Pages. https://doi.org/10.1145/3469013.3469018
```
Thanks to Jason and all who contributed entries to the list.
