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


class Alignments(object):
    filter_props = {'length', 'max_gap', 'min_gap', 'n_gaps', 'score'}
    filter_operators = {'neq', 'gt', 'gte', 'lt', 'lte'}

    def __init__(self, alignments = []):
        if any(not isinstance(a, Alignment) for a in alignments):
            raise TypeError("One or more of the objects is not an Alignment object.")

        self._alignments = alignments

    def __iter__(self):
        for alignment in self._alignments:
            yield alignment

    def __str__(self):
        return str([str(al) for al in self._alignments])

    def __len__(self):
        return len(self._alignments)

    def sort(self, key, reverse=False):
        self._alignments.sort(key=attrgetter(key), reverse=reverse)

    def append(self, alignment):
        if not isinstance(alignment, Alignment):
            raise TypeError("One or more of the objects is not an Alignment object.")

        self._alignments.append(alignment)

    def _get_filter_option(self, kwarg):
        kwarg_list = kwarg.split('__')
        
        if len(kwarg_list) > 2:
            raise TypeError(f'filter() got an unexpected keyword argument {kwarg}.')

        prop = kwarg_list[0]
        operator = kwarg_list[1] if len(kwarg_list) > 1 else None

        if prop not in self.filter_props:
            raise TypeError(f"{prop} is not a valid filter() properties. Valid properties are: {','.join(self.filter_props)}")

        if operator and operator not in self.filter_operators:
            raise TypeError(f"{operator} is not a valid filter() operator. Valid operators are: {','.join(self.filter_operators)}")
        
        return prop, operator

    def _compute_expression(self, alignment, query, value):
        prop, operator = self._get_filter_option(query)

        if not operator:
            return getattr(alignment, prop) == value
        elif operator == 'neq':
            return getattr(alignment, prop) != value
        elif operator == 'gt':
            return getattr(alignment, prop) > value
        elif operator == 'gte':
            return getattr(alignment, prop) >= value
        elif operator == 'lt':
            return getattr(alignment, prop) < value
        elif operator == 'lte':
            return getattr(alignment, prop) <= value
            

    def filter(self, **kwargs):
        filtered_alignments = []
        for alignment in self._alignments:
            is_alignment_wanted = True
            for key, value in kwargs.items():
                is_alignment_wanted = is_alignment_wanted and self._compute_expression(alignment, key, value)

            if is_alignment_wanted:
                filtered_alignments.append(alignment)
        
        return Alignments(filtered_alignments)