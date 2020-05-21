import argparse
from colorama import Fore, Style
from enum import Enum
from itertools import chain
import numpy as np
import os
import pandas as pd
import sys

from alignment import Alignment, Alignments

class Move(Enum):
    HORIZONTAL = '\u2190'
    VERTICAL = '\u2191'
    DIAGONAL = '\u2196'

class Cell:
    def __init__(self, score, indices, origin):
        self.score = score
        self.indices = indices
        self.origin = origin

    def __str__(self):
        return f'{self.origin.value} {self.score}'

    def __eq__(self, other): 
        return self.score == other.score 

    def __ne__(self, other): 
        return not self.__eq__

    def __lt__(self, other): 
        return self.score < other.score 
     
    def __le__(self, other):
        return self.score <= other.score

    def __gt__(self, other): 
        return self.score > other.score 
    
    def __ge__(self, other):
        return self.score >= other.score   

def compute_scoring_matrix(seq1, seq2, match_score, mismatch_score, gap_penalty):
    n = len(seq1) + 1
    m = len(seq2) + 1

    scoring_matrix = [[Cell(0, (i, j), Move.DIAGONAL) for j in range(m)] for i in range(n)]

    for i in range(1, n):
        for j in range(1, m):
            seq_i = seq1[i-1]
            seq_j = seq2[j-1]

            match = Cell(scoring_matrix[i - 1][j - 1].score + (match_score if seq_i == seq_j else mismatch_score), (i,j), Move.DIAGONAL)
            h_gap = Cell(scoring_matrix[i][j - 1].score + gap_penalty, (i,j), Move.HORIZONTAL)
            v_gap = Cell(scoring_matrix[i - 1][j].score + gap_penalty, (i,j), Move.VERTICAL)

            scoring_matrix[i][j] = max(match, h_gap, v_gap, Cell(0, (i, j), Move.DIAGONAL))

    return scoring_matrix

def traceback_process(scoring_matrix, seq1, seq2, starting_cell):
    subseq1, subseq2 = '', ''
    max_gap = 0
    min_gap = max(len(seq1), len(seq2))
    n_gaps = 0
    tmp_gap = None
    actual_cell = starting_cell

    while actual_cell.score > 0:
        i, j = actual_cell.indices
        seq_i = seq1[i - 1]
        seq_j = seq2[j - 1]
        
        if actual_cell.origin == Move.DIAGONAL:
            if tmp_gap:
                max_gap = max(max_gap, tmp_gap)
                min_gap = min(min_gap, tmp_gap) if tmp_gap != 0 else min_gap
                n_gaps += 1
                tmp_gap = None

            subseq1 += seq_i
            subseq2 += seq_j
            actual_cell = scoring_matrix[i-1][j-1]
        else:
            tmp_gap = tmp_gap+1 if tmp_gap else 1
            if actual_cell.origin == Move.HORIZONTAL:
                subseq1 += '-'
                subseq2 += seq_j
                actual_cell = scoring_matrix[i][j-1]
            elif actual_cell.origin == Move.VERTICAL:
                subseq1 += seq_i
                subseq2 += '-'
                actual_cell = scoring_matrix[i-1][j]
            else:
                raise Exception(f'Something went wrong origin must be one of {",".join([move for move in Move])}')
        
    if tmp_gap:
        max_gap = max(max_gap, tmp_gap)
        min_gap = min(min_gap, tmp_gap) if tmp_gap != 0 else min_gap
        n_gaps += 1
        tmp_gap = None
        
    return Alignment(subseq1[::-1], subseq2[::-1], max_gap, min_gap, n_gaps, starting_cell.score, starting_cell.indices)

def printable_matrix(matrix, seq1, seq2):
    df = pd.DataFrame(matrix, index=[(i, c) for i, c in enumerate(' '+seq1)], columns=[(i, c) for i, c in enumerate(' '+seq2)])
    
    return str(df) + '\n\n'

def find_alignments_by_score(scoring_matrix, seq1, seq2):
    alignments = Alignments()
    n, m = len(seq1)+1, len(seq2)+1

    for i in range(1, n):
        for j in range(1, m):
            cell = scoring_matrix[i][j]
            if cell.score > 0:
                alignments.append(traceback_process(scoring_matrix, seq1, seq2, cell))
    
    return alignments

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Implementation of the Smith and Waterman algorithm for local sequence alignment by Daniele Isoni',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('seq1', type=str, help='First input sequence')
    parser.add_argument('seq2', type=str, help='Second input sequence')
    parser.add_argument('--match-score', type=float, default=3.0, help='The score for a sequence match')
    parser.add_argument('--mismatch-score', type=float, help='The score for a sequence mismatch, it is set to negative MATCH_SCORE if not provided')
    parser.add_argument('--gap-penalty', type=float, default=-2.0, help='The penalty for a sequence gap')
    parser.add_argument('--output-file', '-o', type=str, help='Specify file to save the output')
    parser.add_argument('--improvement', action='store_true', help='Prints all alignments with length > 5, score > 4 and gaps > 0')

    args = parser.parse_args()

    seq1 = args.seq1.upper()
    seq2 = args.seq2.upper()
    match_score = args.match_score
    mismatch_score = args.mismatch_score or -match_score
    gap_penalty = args.gap_penalty
    output_file = args.output_file
    improvement = args.improvement

    scoring_matrix = compute_scoring_matrix(seq1, seq2, match_score, mismatch_score, gap_penalty)
    
    max_score_cell = max(chain.from_iterable(scoring_matrix))

    best_alignement = traceback_process(scoring_matrix, seq1, seq2, max_score_cell)

    matrix_to_print = printable_matrix(scoring_matrix, seq1, seq2)

    if output_file:
        if os.path.exists(output_file):
            choice = input(f'The file {output_file} already exists. Do you want to overwrite it? [y/N]\n').lower() or 'n'
            while choice not in ['y', 'yes', 'n', 'no']:
                choice = input(f'{Fore.YELLOW}[WARN] {Style.RESET_ALL}Invalid input. Please enter one of the following: [y/N]\n').lower() or 'n'
            if choice == 'n':
                sys.exit(0)

        f = open(output_file, 'w')
        f.write(matrix_to_print)

    print(matrix_to_print)

    if improvement:
        alignments = find_alignments_by_score(scoring_matrix, seq1, seq2)

        filtered_alignments = alignments.filter(length__gt=5, score__gt=4, min_gap__gt=0)
    
        filtered_alignments.sort(key='score', reverse=True)

        for al in filtered_alignments:
            if output_file:
                f.write(al.to_string(to_file=True) + '\n')
            print(al)
    else:
        out_string = f'''seq1: {seq1}
seq2: {seq2}
{best_alignement}
'''
        if output_file:
            f.write(out_string)
        print(out_string)
        

