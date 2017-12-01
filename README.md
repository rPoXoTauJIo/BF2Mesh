BF2Mesh - Battlefield 2 mesh file parser

This code documents how to parse mesh files of the DICE/EA games Battlefield 2,
Battlefield 2142, Battlefield Heroes, Battlefield Play4Free, which share the
same internal layout. These files typically have the extension ".StaticMesh",
".BundledMesh" or ".SkinnedMesh".

The code does not include rendering code or otherwise convert or output the data
to file.
Examples at unittests(use ``nosetests`` for running tests).

For more information, see: http://www.bytehazard.com