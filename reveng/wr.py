import claripy
from natsort import natsorted

import values

# This represents a weird register in a weird function
class WeirdRegister:
    def __init__(self, location):
        self.location = location
    
    def get_value(self):
        return self.value if hasattr(self, "value") else None

    def set_value(self, value):
        assert isinstance(value, values.AbstractValue), f"value is not a possible value ({value})"
        self.value = value

    def get_dual(self):
        return self.dual if hasattr(self, "dual") else None

    def set_dual(self, dual):
        assert isinstance(dual, WeirdRegister), f"Dual is not a weird register"
        self.dual = dual

class WeirdRegisterCollection:
    def __init__(self):
        self.wrs = {}

    def add(self, location: int):
        wr = WeirdRegister(location)
        self.wrs[location] = wr
        return wr

    def find(self, location: int):
        if not location in self.wrs: return None
        return self.wrs[location]

    def iterator(self):
        return self.wrs.values()

class WeirdRegisterReader:
    def __init__(self):
        self.start_time = None
        self.mem_access = None
        self.end_time = None

        self.saved = False
        self.timer_index = 0

        self.map = {}

    def start_timer(self, symbol):
        self.saved = False
        self.start_time = symbol

    def end_timer(self, symbol):
        self.saved = False
        self.end_time = symbol

    def record_instr(self):
        self.saved = True

    def is_instr_recorded(self):
        return self.saved

    def record_memaccess(self, address):
        self.mem_access = address

    def record_memaccess_conditional(self, address):
        if self.has_timer_started():
            self.record_memaccess(address)
            return True
        return False

    def timer(self, symbol):
        if self.start_time is None:
            self.start_timer(symbol)
        elif self.end_time is None:
            self.end_timer(symbol)
            if self.mem_access is not None:
                self.map[(self.start_time, self.end_time)] = self.mem_access
                self.start_time = None
                self.end_time = None
                self.mem_access = None
            else:
                self.start_timer(symbol)

    def find(self, symbols):
        assert all(s.op == "BVS" for s in symbols), f"One symbol is not a symbol but an expression"
        # Sort symbols by name: exploit the incremental claripy name
        symbols = tuple(sorted(symbols, key=lambda s: s.args[0]))
        if not symbols in self.map:
            if len(symbols) == 2:
                symbols = symbols[1], symbols[0]
            else:
                symbols = tuple(natsorted(symbols, key=lambda s: s.args[0]))


        return self.map[symbols] if symbols in self.map else None

    def is_map_empty(self):
        return len(self.map) == 0
    
    def has_timer_started(self):
        return not self.is_map_empty() or self.start_time is not None

    def rdtscx_hook(self, state):
        tsc = claripy.BVS(f"timestamp_{self.timer_index:09d}", 64)
        lo = claripy.Extract(31, 0, tsc)
        hi = claripy.Extract(63, 32, tsc)
        state.regs.rdx = claripy.ZeroExt(32, hi)
        state.regs.rax = claripy.ZeroExt(32, lo)
        self.timer_index += 1

        self.timer(tsc)

# This represents a symbolic location of a weird register in a weird gate
class RegisterLocation:
    index = 0
    # expr: expression of the location
    def __init__(self, expr):
        self.index = RegisterLocation.index
        self.expr = expr
        RegisterLocation.index += 1

    def get_str_repr(self):
        invs = 'o' if self.inverted is None else ('~' if self.inverted else '')
        return f"{invs}{self.expr}"

    def eval(self, state, symbolic_registers):
        # Take the inverse of the map, so I get variable -> reg_name
        new_expr = self.expr
        for r in symbolic_registers:
            new_expr = claripy.replace(new_expr, symbolic_registers[r], getattr(state.regs, r))
        new_expr = claripy.simplify(new_expr)
        assert new_expr.concrete, \
            f"If {self.expr} is the location of a Weird Register in a gate, now" \
            "it should be concrete, but it is {new_expr}"
        return new_expr.concrete_value

    def is_input(self):
        return not self.is_output()

    def is_output(self):
        raise NotImplemented()

    def is_inverted(self):
        return self.inverted

    def set_inverted(self, inv):
        self.inverted = inv

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index

class InputRegisterLocation(RegisterLocation):
    def is_output(self):
        return False

class OutputRegisterLocation(RegisterLocation):
    def is_output(self):
        return True
