# LocalSequenceAlignment-SmithWaterman
A python implementation of the local sequence alignment algorithm by Smith and Waterman

The main file is the smith_waterman.py which contains the core of the algorithm.
The alignment.py contains some classes created to manage better of the data structures throughout the algorithm.

# Installation

Run
``` pip install -r requirements.txt ```

# Usage

Here is the output for the command `python smith_waterman.py -h`

```
usage: smith_waterman.py [-h] [--match-score MATCH_SCORE]
                         [--mismatch-score MISMATCH_SCORE]
                         [--gap-penalty GAP_PENALTY]
                         [--output-file OUTPUT_FILE] [--all-alignments]
                         seq1 seq2

Implementation of the Smith and Waterman algorithm for local sequence
alignment by Daniele Isoni

positional arguments:
  seq1                  First input sequence
  seq2                  Second input sequence

optional arguments:
  -h, --help            show this help message and exit
  --match-score MATCH_SCORE
                        The score for a sequence match (default: 3.0)
  --mismatch-score MISMATCH_SCORE
                        The score for a sequence mismatch, it is set to
                        negative MATCH_SCORE if not provided (default: None)
  --gap-penalty GAP_PENALTY
                        The penalty for a sequence gap (default: -2.0)
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        Specify file to save the output (default: None)
  --all-alignments      Prints all alignments (default: False)
```

Examples:
- `py smith_waterman.py TGTTACGG GGTTGACTA`
- `py smith_waterman.py TGTTACGG GGTTGACTA --match-score=5 --mismatch-score=-5 --gap-penalty=-3 --all-alignments -o=results.txt`