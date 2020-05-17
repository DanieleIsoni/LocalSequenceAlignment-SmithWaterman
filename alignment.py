from operator import attrgetter
from colorama import Fore, Style

class Alignment:
    def __init__(self, subseq1, subseq2, max_gap, min_gap, n_gaps, score, indexes):

        if len(subseq1) != len(subseq2):
            raise ValueError("Something went wrong, the two subsequences are not the same length")
        
        self.subseq1 = subseq1
        self.subseq2 = subseq2
        self.length = len(subseq1)
        self.max_gap = max_gap
        self.min_gap = min_gap
        self.n_gaps = n_gaps
        self.score = score
        self.indexes = indexes
    
    def _colored_subsequences(self):
        string1 = ''
        string2 = ''
        for c1, c2 in zip(self.subseq1, self.subseq2):
            if c1 == c2:
                string1 += Fore.GREEN + c1
                string2 += Fore.GREEN + c2
            else:
                string1 += Fore.RED + c1
                string2 += Fore.RED + c2
        return f'{string1}\n{string2}{Style.RESET_ALL}'

    def to_string(self, to_file=False):
        alignment_string = f'score: {self.score}\n'
        if to_file:
            alignment_string += self.subseq1 + '\n' + self.subseq2
        else:
            alignment_string += self._colored_subsequences()
        
        return f'''{alignment_string}
max_gap: {self.max_gap}
min_gap: {self.min_gap}
n_gaps: {self.n_gaps}
trace_back_start_indexes: {self.indexes}
'''

    def __str__(self):
        return self.to_string()