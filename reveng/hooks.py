import random

import angr
import claripy
from angr.concretization_strategies.base import SimConcretizationStrategy

# This tracks argument dereferences
class ArgTracker:
    def __init__(self):
        self.map = {}

    def find(self, symbol):
        visited = set()
        variables = tuple(symbol.variables)
        assert len(variables) == 1, f"symbol is not a symbol ({symbol})"
        symbol_name = variables[0]
        while True:
            assert symbol not in visited, f"Loop detected in map"
            visited.add(symbol)
            if not symbol in self.map: return symbol
            else: symbol = self.map[symbol]

        raise Exception("This should be unreacheable")

    def get_map(self):
        return self.map

    def mem_access(self, state):
        addr = state.inspect.mem_read_address
        expr = state.inspect.mem_read_expr
        if state.solver.symbolic(addr):
            self.map[expr] = addr

class SimConcretizationForWeirdRegisters(SimConcretizationStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.concretized_addrs = []

    # NOTE: in order to concretize symbolic memory accesses, we take the
    #       minimum value the symbol can hold
    def _concretize(self, memory, addr, **kwargs):
        m = memory.state.solver.min(addr)
        self.concretized_addrs.append(m)
        return [m]
