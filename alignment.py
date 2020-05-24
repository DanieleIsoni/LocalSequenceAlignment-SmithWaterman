from operator import attrgetter
from typing import Any, Iterator, List

from colorama import Fore, Style


class Alignment:
    """Represents an alignment.

    Attributes:
        subseq1 (str): The first subsequence of the alignment
        subseq2 (str): The second subsequence of the alignment
        length (int): The length of the alignment
        num_matches (int): The number of matches in the alignment
        num_mismatches (int): The number of mismatches in the alignment
        max_gap (int): The size of the biggest gap found in the alignment
        min_gap (int): The size of the smaller gap found in the alignment
        n_gaps (int): The number of gaps found in the alignment
        score (float): The score of the alignment
        indices ((int, int)): The starting indices for the traceback of the alignment
    """

    def __init__(
        self,
        subseq1: str,
        subseq2: str,
        max_gap: int,
        min_gap: int,
        n_gaps: int,
        score: float,
        indices: (int, int),
    ) -> None:
        """
        Args:
        subseq1 (str): The first subsequence of the alignment
        subseq2 (str): The second subsequence of the alignment
        max_gap (int): The size of the biggest gap found in the alignment
        min_gap (int): The size of the smaller gap found in the alignment
        n_gaps (int): The number of gaps found in the alignment
        score (float): The score of the alignment
        indices ((int, int)): The starting indices for the traceback of the alignment
        """

        if len(subseq1) != len(subseq2):
            raise ValueError("Something went wrong, the two subsequences are not the same length")

        self.subseq1 = subseq1
        self.subseq2 = subseq2
        self.length = len(subseq1)
        self.num_matches = sum([a == b for a, b in zip(subseq1, subseq2)])
        self.num_mismatches = sum(["-" not in [a, b] and a != b for a, b in zip(subseq1, subseq2)])
        self.max_gap = max_gap
        self.min_gap = min_gap
        self.n_gaps = n_gaps
        self.score = score
        self.indices = indices

    def _colored_subsequences(self) -> str:
        """This method is needed to provied a colored output to the console"""
        string1 = ""
        string2 = ""
        for c1, c2 in zip(self.subseq1, self.subseq2):
            if c1 == c2:
                string1 += Fore.GREEN + c1
                string2 += Fore.GREEN + c2
            elif "-" in [c1, c2]:
                string1 += Fore.YELLOW + c1
                string2 += Fore.YELLOW + c2
            else:
                string1 += Fore.RED + c1
                string2 += Fore.RED + c2
        return f"{string1}\n{string2}{Style.RESET_ALL}"

    def to_string(self, to_file: bool = False) -> str:
        """This is needed to provied an output string that is colored if not to be printed to file.

        Args:
            to_file (bool): if True the output will not be colored.
        """

        alignment_string = f"score: {self.score}\n"
        if to_file:
            alignment_string += self.subseq1 + "\n" + self.subseq2
        else:
            alignment_string += self._colored_subsequences()

        return f"""{alignment_string}
length: {self.length}
num_matches: {self.num_matches}
num_mismatches: {self.num_mismatches}
max_gap_length: {self.max_gap}
min_gap_length: {self.min_gap}
n_gaps: {self.n_gaps}
trace_back_start_indices: {self.indices}
"""

    def __str__(self) -> str:
        return self.to_string()


class Alignments(object):
    """Represents a list of alignments

    This has been created to have a structure to manage better the alignments found.

    Attributes:
        alignments (:obj:`list` of Alignment): This is the actual list of alignments
    """

    def __init__(self, alignments: List[Alignment] = []) -> None:
        if any(not isinstance(a, Alignment) for a in alignments):
            raise TypeError("One or more of the objects is not an Alignment object.")

        self._alignments = alignments

    def __iter__(self) -> Iterator[Alignment]:
        """This allows to iterate through this object"""

        for alignment in self._alignments:
            yield alignment

    def __str__(self) -> str:
        return str([str(al) for al in self._alignments])

    def __len__(self) -> int:
        return len(self._alignments)

    def sort(self, key: str, reverse: bool = False) -> None:
        """Used to sort inplace the alignment list"""

        self._alignments.sort(key=attrgetter(key), reverse=reverse)

    def append(self, alignment: Alignment) -> None:
        """Used to add to the end of the list a new alignment"""

        if not isinstance(alignment, Alignment):
            raise TypeError("One or more of the objects is not an Alignment object.")

        self._alignments.append(alignment)
