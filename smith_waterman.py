import argparse
import os
import re
import sys
from enum import Enum
from itertools import chain
from typing import List

import pandas as pd
from colorama import Fore, Style

from alignment import Alignment, Alignments


class Move(Enum):
    """This enum represents the possible directions for the choices while computing the scoring matrix
    """

    HORIZONTAL = "\u2190"
    VERTICAL = "\u2191"
    DIAGONAL = "\u2196"


class Cell:
    """This represents a cell of the scoring matrix

    Attributes:
        score (float): the score of the amino acid pair
        indices ((int, int)): the indices of the Cell
        origin (Move): the direction for the traceback process
    """

    def __init__(self, score: float, indices: (int, int), origin: Move) -> None:
        """
        Args:
            score (float): the score of the amino acid pair
            indices ((int, int)): the indices of the Cell
            origin (Move): the direction for the traceback process
        """
        self.score = score
        self.indices = indices
        self.origin = origin

    def __str__(self) -> str:
        return f"{self.origin.value} {self.score}"

    # The following methods are used for comparing Cells by score
    def __eq__(self, other: "Cell") -> bool:
        return self.score == other.score

    def __ne__(self, other: "Cell") -> bool:
        return not self.__eq__

    def __lt__(self, other: "Cell") -> bool:
        return self.score < other.score

    def __le__(self, other: "Cell") -> bool:
        return self.score <= other.score

    def __gt__(self, other: "Cell") -> bool:
        return self.score > other.score

    def __ge__(self, other: "Cell") -> bool:
        return self.score >= other.score


def compute_scoring_matrix(
    seq1: str, seq2: str, match_score: float, mismatch_score: float, gap_penalty: float
) -> List[List[Cell]]:
    """This method is used to compute the scoring matrix for
    Args:
        seq1 (str): the first sequence
        seq2 (str): the second sequence
        match_score (float): the score for the match
        mismatch_score (float): the score for the mismatch
        gap_penalty (float): the penalty fot the gap
    Returns:
        the matrix containing cell content
    """
    n = len(seq1) + 1
    m = len(seq2) + 1

    # Initialize the scoring matrix
    scoring_matrix = [[Cell(0, (i, j), Move.DIAGONAL) for j in range(m)] for i in range(n)]

    for i in range(1, n):
        for j in range(1, m):
            seq_i = seq1[i - 1]
            seq_j = seq2[j - 1]

            # Compute the scoring for match/mismatch and gaps
            match = Cell(
                scoring_matrix[i - 1][j - 1].score
                + (match_score if seq_i == seq_j else mismatch_score),
                (i, j),
                Move.DIAGONAL,
            )
            h_gap = Cell(scoring_matrix[i][j - 1].score + gap_penalty, (i, j), Move.HORIZONTAL)
            v_gap = Cell(scoring_matrix[i - 1][j].score + gap_penalty, (i, j), Move.VERTICAL)

            # Store the result in the matrix
            scoring_matrix[i][j] = max(match, h_gap, v_gap, Cell(0, (i, j), Move.DIAGONAL))

    return scoring_matrix


def traceback_process(
    scoring_matrix: List[List[Cell]], seq1: str, seq2: str, starting_cell: Cell
) -> Alignment:
    """This method computes the traceback process for retrieving an alignment
    Args:
        scoring_matrix (List[List[Cell]]): the scoring matrix
        seq1 (str): the first sequence
        seq2 (str): the second sequence
        starting_cell (Cell): the starting cell for the traceback process
    Returns:
        The alignment starting from starting_cell
    """
    subseq1, subseq2 = "", ""
    max_gap = 0
    min_gap = max(len(seq1), len(seq2))
    n_gaps = 0
    tmp_gap = None
    gap_direction = None
    actual_cell = starting_cell

    while actual_cell.score > 0:
        i, j = actual_cell.indices
        seq_i = seq1[i - 1]
        seq_j = seq2[j - 1]

        if actual_cell.origin == Move.DIAGONAL:
            if tmp_gap is not None:
                # If there was a gap end it and update counts
                max_gap = max(max_gap, tmp_gap)
                min_gap = min(min_gap, tmp_gap)
                n_gaps += 1
                tmp_gap = None
                gap_direction = None

            subseq1 += seq_i
            subseq2 += seq_j
            actual_cell = scoring_matrix[i - 1][j - 1]
        elif actual_cell.origin == Move.HORIZONTAL:
            if gap_direction == Move.HORIZONTAL:
                tmp_gap += 1
            else:
                if tmp_gap is not None:
                    max_gap = max(max_gap, tmp_gap)
                    min_gap = min(min_gap, tmp_gap)
                    n_gaps += 1
                tmp_gap = 1
                gap_direction = Move.HORIZONTAL

            subseq1 += "-"
            subseq2 += seq_j
            actual_cell = scoring_matrix[i][j - 1]
        elif actual_cell.origin == Move.VERTICAL:
            if gap_direction == Move.VERTICAL:
                tmp_gap += 1
            else:
                if tmp_gap is not None:
                    max_gap = max(max_gap, tmp_gap)
                    min_gap = min(min_gap, tmp_gap)
                    n_gaps += 1
                tmp_gap = 1
                gap_direction = Move.VERTICAL

            subseq1 += seq_i
            subseq2 += "-"
            actual_cell = scoring_matrix[i - 1][j]
        else:
            raise Exception(
                f'Something went wrong origin must be one of {",".join([move for move in Move])}'
            )

    if tmp_gap is not None:
        max_gap = max(max_gap, tmp_gap)
        min_gap = min(min_gap, tmp_gap)
        n_gaps += 1

    return Alignment(
        subseq1[::-1],
        subseq2[::-1],
        max_gap,
        min_gap,
        n_gaps,
        starting_cell.score,
        starting_cell.indices,
    )


def printable_matrix(matrix: List[list], seq1: str, seq2: str) -> str:
    """This prints the matrix in a readable format
    Args:
        matrix (List[list]): the matrix to be printed
        seq1 (str):
        seq2 (str):
    Returns:
        The printable string
    """
    df = pd.DataFrame(
        matrix,
        index=[(i, c) for i, c in enumerate(" " + seq1)],
        columns=[(i, c) for i, c in enumerate(" " + seq2)],
    )

    return str(df) + "\n\n"


def find_alignments_by_score(scoring_matrix: List[List[Cell]], seq1: str, seq2: str) -> Alignments:
    """This method computes all the alignments for a given scoring matrix
    Args:
        scoring_matrix (List[List[Cell]]): the scoring matrix
        seq1 (str): the first sequence
        seq2 (str): the second sequence
    Returns:
        All the alignments from the scoring matrix without overlap
    """
    alignments = Alignments()
    n, m = len(seq1) + 1, len(seq2) + 1

    for i in range(1, n):
        for j in range(1, m):
            cell = scoring_matrix[i][j]
            if cell.score > 0:
                alignments.append(traceback_process(scoring_matrix, seq1, seq2, cell))

    return alignments


def sequence_arg(value):
    """
    Validate the seq1 or seq2 argument
    Function will ensure that the arguments matches a given regex that allows
    only characters from A, C, G, T.

    Args:
        value (str): automatically passed by the ArgumentParser object
    Returns:
    Returns the value back to the ArgumentParser object
    Exceptions:
        argparse.ArgumentTypeError - if the passed argument doesn't match the regex
    """
    # Regex check
    if not re.match("^[ACTGactg]+$", value):
        raise argparse.ArgumentTypeError(
            "must contain only amino acids from the following list: A, C, G, T"
        )

    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Implementation of the Smith and Waterman algorithm for local sequence alignment by Daniele Isoni",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "seq1",
        type=sequence_arg,
        help="First input sequence (must contain only amino acids from the following list: A, C, G, T)",
    )
    parser.add_argument(
        "seq2",
        type=sequence_arg,
        help="Second input sequence (must contain only amino acids from the following list: A, C, G, T)",
    )
    parser.add_argument(
        "--match-score", type=float, default=3.0, help="The score for a sequence match"
    )
    parser.add_argument(
        "--mismatch-score",
        type=float,
        help="The score for a sequence mismatch, it is set to negative MATCH_SCORE if not provided",
    )
    parser.add_argument(
        "--gap-penalty", type=float, default=-2.0, help="The penalty for a sequence gap"
    )
    parser.add_argument("--output-file", "-o", type=str, help="Specify file to save the output")
    parser.add_argument(
        "--all-alignments", action="store_true", help="Prints all alignments",
    )

    args = parser.parse_args()

    seq1 = args.seq1.upper()
    seq2 = args.seq2.upper()
    match_score = args.match_score
    mismatch_score = args.mismatch_score or -match_score
    gap_penalty = args.gap_penalty
    output_file = args.output_file
    all_alignments = args.all_alignments

    scoring_matrix = compute_scoring_matrix(seq1, seq2, match_score, mismatch_score, gap_penalty)

    max_score_cell = max(chain.from_iterable(scoring_matrix))

    best_alignement = traceback_process(scoring_matrix, seq1, seq2, max_score_cell)

    matrix_to_print = printable_matrix(scoring_matrix, seq1, seq2)

    if output_file:
        # If the file exists ask the user if he wants to overwrite the file
        if os.path.exists(output_file):
            choice = (
                input(
                    f"The file {output_file} already exists. Do you want to overwrite it? [y/N]\n"
                ).lower()
                or "n"
            )
            while choice not in ["y", "yes", "n", "no"]:
                choice = (
                    input(
                        f"{Fore.YELLOW}[WARN] {Style.RESET_ALL}Invalid input. Please enter one of the following: [y/N]\n"
                    ).lower()
                    or "n"
                )
            if choice == "n":
                sys.exit(0)

        f = open(output_file, "w")
        f.write(matrix_to_print)

    print(matrix_to_print)

    if all_alignments:
        alignments = find_alignments_by_score(scoring_matrix, seq1, seq2)

        alignments.sort(key="score", reverse=True)

        for al in alignments:
            if output_file:
                f.write(al.to_string(to_file=True) + "\n")
            print(al)
    else:
        out_string = f"""seq1: {seq1}
seq2: {seq2}
{best_alignement}
"""
        if output_file:
            f.write(out_string)
        print(out_string)
