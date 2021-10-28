#!/bin/bash -e

./sinusgen.py -cfg sinus1.json -show

exit 0
sinusgen v2.32 [27.10.2021] *** by fieserWolF
usage: sinusgen.py [-h] [-cfg CONFIG_FILE] [-show] [-list] [-output OUTPUT_FILE] [-min MINIMUM_VALUE] [-max MAXIMUM_VALUE] [-steps STEPS]
                    [-type TYPE] [-invert] [-offset OFFSET] [-mod MODULO]

This program writes sinus data as bytes into a binary file. If values are greater than 256, two files are written.

optional arguments:
  -h, --help           show this help message and exit
  -cfg CONFIG_FILE     configuration in .json format
  -show                show preview
  -list                list all avaiable sinus types and exit
  -output OUTPUT_FILE  name of binary output file without its suffix
  -min MINIMUM_VALUE   minimum value (0-65535)
  -max MAXIMUM_VALUE   maximum value (0-65535)
  -steps STEPS         amount of bytes to generate, values below 5 cause an error with some sinus-types
  -type TYPE           sinus type, see output of --list
  -invert              invert values
  -offset OFFSET       step offset, where to begin
  -mod MODULO          modulo value

Note: All values of a config-file can be overwritten by commandline parameters.

Examples:
    ./sinusgen.py -cfg sinus1.json -show
    ./sinusgen.py -output datafile -min 0 -max 255 -steps 256 -type 1 -invert -offset 20 -mod 8
    ./sinusgen.py -cfg sinus1.json -max 255 -type 10 -show


Available sinus types:
 0 : "full sinus"
 1 : "half sinus"
 2 : "shot"
 3 : "boobs"
 4 : "small hill, big hill"
 5 : "high valleys"
 6 : "three hills"
 7 : "three irregulars"
 8 : "four brothers"
 9 : "wave shot"
10 : "zig zag"
11 : "double trouble"
12 : "what the heck"
13 : "landscape"
14 : "two hills"
15 : "whatever"
16 : "the famous Mr Ed"
17 : "curly"
18 : "Oh dear..."
19 : "When will it end?"
20 : "ice cream"
21 : "good grief..."
22 : "nonsense"
23 : "windy"
24 : "one more to go"
25 : "Thanks God it`s over."


example.json
------------
{
    "output": "sinus1",
    "min": 0,
    "max": 255,
    "steps": 256,
    "type" : 12,
    "invert" : 0,
    "offset" : 0,
    "mod" : 0,
    "comment" : "steps-values below 5 cause an error with some sinus-types"
}
