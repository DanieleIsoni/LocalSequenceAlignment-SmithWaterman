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
                         [--sort {num_mismatches,n_gaps,score,max_gap_length,min_gap_length,length,num_matches}]
                         [--reverse-sort] [--output-file OUTPUT_FILE]
                         [--num-mismatches NUM_MISMATCHES]
                         [--num-mismatches-operator {eq,neq,gt,gte,lt,lte}]
                         [--n-gaps N_GAPS]
                         [--n-gaps-operator {eq,neq,gt,gte,lt,lte}]
                         [--score SCORE]
                         [--score-operator {eq,neq,gt,gte,lt,lte}]
                         [--max-gap-length MAX_GAP_LENGTH]
                         [--max-gap-length-operator {eq,neq,gt,gte,lt,lte}]
                         [--min-gap-length MIN_GAP_LENGTH]
                         [--min-gap-length-operator {eq,neq,gt,gte,lt,lte}]
                         [--length LENGTH]
                         [--length-operator {eq,neq,gt,gte,lt,lte}]
                         [--num-matches NUM_MATCHES]
                         [--num-matches-operator {eq,neq,gt,gte,lt,lte}]
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
  --sort {num_mismatches,n_gaps,score,max_gap_length,min_gap_length,length,num_matches}
                        The parameter by which alignments will be sorted
                        (default: None)
  --reverse-sort        If this is specified alignments sort will be reversed
                        (default: False)
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        Specify file to save the output (default: None)
  --num-mismatches NUM_MISMATCHES
                        Specify this parameter to filter by num_mismatches
                        (default: None)
  --num-mismatches-operator {eq,neq,gt,gte,lt,lte}
                        Specify this parameter to filter by num_mismatches
                        NUM_MISMATCHES_OPERATOR value (default: eq)
  --n-gaps N_GAPS       Specify this parameter to filter by n_gaps (default:
                        None)
  --n-gaps-operator {eq,neq,gt,gte,lt,lte}
                        Specify this parameter to filter by n_gaps
                        N_GAPS_OPERATOR value (default: eq)
  --score SCORE         Specify this parameter to filter by score (default:
                        None)
  --score-operator {eq,neq,gt,gte,lt,lte}
                        Specify this parameter to filter by score
                        SCORE_OPERATOR value (default: eq)
  --max-gap-length MAX_GAP_LENGTH
                        Specify this parameter to filter by max_gap_length
                        (default: None)
  --max-gap-length-operator {eq,neq,gt,gte,lt,lte}
                        Specify this parameter to filter by max_gap_length
                        MAX_GAP_LENGTH_OPERATOR value (default: eq)
  --min-gap-length MIN_GAP_LENGTH
                        Specify this parameter to filter by min_gap_length
                        (default: None)
  --min-gap-length-operator {eq,neq,gt,gte,lt,lte}
                        Specify this parameter to filter by min_gap_length
                        MIN_GAP_LENGTH_OPERATOR value (default: eq)
  --length LENGTH       Specify this parameter to filter by length (default:
                        None)
  --length-operator {eq,neq,gt,gte,lt,lte}
                        Specify this parameter to filter by length
                        LENGTH_OPERATOR value (default: eq)
  --num-matches NUM_MATCHES
                        Specify this parameter to filter by num_matches
                        (default: None)
  --num-matches-operator {eq,neq,gt,gte,lt,lte}
                        Specify this parameter to filter by num_matches
                        NUM_MATCHES_OPERATOR value (default: eq)
```

Examples:
- `py smith_waterman.py TGTTACGG GGTTGACTA`
- `py smith_waterman.py TGTTACGG GGTTGACTA --match-score=5 --mismatch-score=-5 --gap-penalty=-3 -o=results.txt`
- `py smith_waterman.py TGTTACGG GGTTGACTA --length=5 --length-operator=gt --score=3 --score-operator=gt --sort=length --reverse-sort` This returns all the alignments, ordered by decreasing alignment length, with length > 5 and score > 3