import utils
from itertools import product

class DNF:
    # formula is a list of terms to be ORed together
    # a sublist in a formula is a list of terms to be ANDed together
    # a positive value indicates a variable
    # a negative value indicates the NOT of a variable
    # I expect NO numbers: only lists
    # A simple OR is indicated with a list of one element
    def __init__(self, formula):
        self.formula = formula

    # values: dictionary: variable -> value
    def compute(self, values):
        expr_value = 0
        for term in self.formula:
            term_value = 1
            for v in term:
                val = values[v]
                term_value *= val
            expr_value = max(min(term_value + expr_value, 1), 0)
        return expr_value

    def list_variables(self):
        return {r for minterm in self.formula for r in minterm}

    # Returns True if this DNF is an identity
    # i.e., if O = I
    def is_identity(self):
        return len(self.formula) == 1 and len(self.formula[0]) == 1

class TruthTable:
    def __init__(self, dnf, m):
        self.dnf = dnf
        self.m = m

    # m: map from a RegisterLocation to a weird register
    def compute(self, translate_variables=True):
        m = self.m
        im = utils.invert_map(m)
        assignment = {}
        all_variables = [rl for rl in self.m]
        # Divide in inverted and non-inverted
        noninv_variables = [v for v in all_variables if m[v].get_value().is_inverted() == False]
        inv_variables = [v for v in all_variables if m[v].get_value().is_inverted() == True]
        # Assign values to the noninv_variables
        values_numeric = product((0,1), repeat=len(noninv_variables))
        outputs = {}
        for v in values_numeric:
            noninv_values = {var: vn for var, vn in zip(noninv_variables, v)}
            inv_values = {}
            for r in noninv_variables:
                if r in m and m[r].get_dual() in im:
                    inv_values[im[m[r].get_dual()]] = 1 - noninv_values[r]
            fixed_values = {r: m[r].get_value() for r in m if r.is_input() and m[r].get_value().is_fixed()}
            computed_output = self.dnf.compute(noninv_values | inv_values | fixed_values)
            outputs[v] = computed_output
        if translate_variables:
            noninv_variables = [m[v] for v in noninv_variables]
        return noninv_variables, outputs
