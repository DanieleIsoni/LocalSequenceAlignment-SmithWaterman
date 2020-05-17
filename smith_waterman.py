import argparse
from colorama import Fore, Style
import numpy as np
import os
import pandas as pd
import sys

from alignment import Alignment

def compute_scoring_matrix(seq1, seq2, match_score, mismatch_score, gap_penalty):
    n = len(seq1) + 1
    m = len(seq2) + 1

    scoring_matrix = np.zeros((n, m))

    for i in range(1, n):
        for j in range(1, m):
            seq_i = seq1[i-1]
            seq_j = seq2[j-1]

            match = scoring_matrix[i - 1, j - 1] + (match_score if seq_i == seq_j else mismatch_score)
            h_gap = scoring_matrix[i, j - 1] + gap_penalty
            v_gap = scoring_matrix[i - 1, j] + gap_penalty

            scoring_matrix[i, j] = max(match, v_gap, h_gap, 0)

    return scoring_matrix

def get_max_score_indexes(scoring_matrix):
    return np.unravel_index(np.argmax(scoring_matrix, axis=None), scoring_matrix.shape)

def traceback_process(scoring_matrix, seq1, seq2, max_indexes):
    subseq1, subseq2 = '', ''
    max_gap = 0
    min_gap = max(len(seq1), len(seq2))
    n_gaps = 0
    i_gap = 0
    j_gap = 0
    score = scoring_matrix[max_indexes]
    starting_indexes = max_indexes

    while scoring_matrix[max_indexes] > 0:
        i = max_indexes[0]
        j = max_indexes[1]
        seq_i = seq1[i - 1]
        seq_j = seq2[j - 1]
        
        if seq_i == seq_j:
            if i_gap != 0:
                min_gap = min(min_gap, i_gap)
                max_gap = max(max_gap, i_gap)
                n_gaps += 1
            if j_gap != 0:
                min_gap = min(min_gap, j_gap)
                max_gap = max(max_gap, j_gap)
                n_gaps += 1
            i_gap, j_gap = 0, 0

            subseq1 += seq_i
            subseq2 += seq_j
            max_indexes = (i-1, j-1)
        elif scoring_matrix[i-1, j] > scoring_matrix[i, j-1]:
            if i_gap != 0:
                min_gap = min(min_gap, i_gap)
                max_gap = max(max_gap, i_gap)
                n_gaps += 1
                i_gap = 0
            j_gap += 1

            subseq1 += seq_i
            subseq2 += '-'
            max_indexes = (i-1, j)
        else:
            if j_gap != 0:
                min_gap = min(min_gap, j_gap)
                max_gap = max(max_gap, j_gap)
                n_gaps += 1
                j_gap = 0
            i_gap += 1
            
            subseq1 += '-'
            subseq2 += seq_j
            max_indexes = (i, j-1)
        
    return Alignment(subseq1[::-1], subseq2[::-1], max_gap, min_gap, n_gaps, score, starting_indexes)

def printable_matrix(matrix, seq1, seq2):
    df = pd.DataFrame(matrix, index=[(i, c) for i, c in enumerate(' '+seq1)], columns=[(i, c) for i, c in enumerate(' '+seq2)])
    
    return str(df) + '\n\n'

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

    args = parser.parse_args()

    seq1 = args.seq1.upper()
    seq2 = args.seq2.upper()
    match_score = args.match_score
    mismatch_score = args.mismatch_score or -match_score
    gap_penalty = args.gap_penalty
    output_file = args.output_file

    scoring_matrix = compute_scoring_matrix(seq1, seq2, match_score, mismatch_score, gap_penalty)
    
    max_indexes = get_max_score_indexes(scoring_matrix)

    best_alignement = traceback_process(scoring_matrix, seq1, seq2, max_indexes)

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

    out_string = f'''seq1: {seq1}
seq2: {seq2}
{best_alignement}
'''
    if output_file:
        f.write(out_string)
    print(out_string)
        

