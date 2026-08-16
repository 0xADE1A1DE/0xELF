import claripy

from weirdgate import WiredWeirdGate

# NOTE: we support only expressions of type arg + Y
class ArgumentsCollection:
    # args: dictionary that maps a name to an Arg object
    def __init__(self, args):
        self.args = args
        # Dictionary that associates
        # (arg_index, arg_offset)
        # to an Argument object
        self.arguments = {}

    def get(self, expr, do_not_add=False):
        # Find the argument in expr
        variables = tuple(expr.variables)
        assert len(variables) == 1, f"{expr} is treated as an argument, but contains more than one variable"
        argname = variables[0]
        assert argname in self.args
        arg = self.args[argname]
        argsymbol = arg.symbol
        
        # Get offset
        solver = claripy.Solver()
        new_expr = claripy.replace(expr, argsymbol, claripy.BVV(0, 64))
        offset = solver.eval(claripy.simplify(new_expr), 1)[0]

        # Check if Argument exists or add a new Argument
        key = (arg.index, offset)

        if key in self.arguments:
            value = self.arguments[key]
        elif not do_not_add:
            value = Argument(arg, offset)
            self.arguments[key] = value
        else:
            return None
        return value

# This class represents a value for a weird register
class AbstractValue:
    def __init__(self):
        pass

    def __str__(self):
        raise NotImplemented()

    def is_inverted(self):
        raise NotImplemented()

    def is_fixed(self):
        return False

    def complementary(self, other):
        raise NotImplemented()

# This class represents a concrete value for a weird register
# value: the concrete number for a weird register
class Value(AbstractValue):
    def __init__(self, value: int):
        super().__init__()
        assert value == 0 or value == 1, f"A weird register is only one bit: " \
            "{value} cannot be represented with one bit"
        self.value = value

    def __str__(self):
        return str(self.value)

    def is_inverted(self):
        return None

    def is_fixed(self):
        return True
    
    def __eq__(self, other):
        return isinstance(other, Value) and other.value == self.value

    def complementary(self, other):
        if not isinstance(other, Value): return False
        return self.value != other.value

# This class represents an argument given to a weird function
class Arg:
    # index: index of the argument in the function input
    # variable: the claripy variable representing this argument
    def __init__(self, index: int, variable: claripy.ast.bv.BV):
        super().__init__()
        self.index = index
        self.symbol = variable

    def __str__(self):
        return f"arg{self.index} ({self.symbol})"

    def byte(self):
        return 0

    # NOTE: I expect Args to be properly initialized.
    def __eq__(self, other):
        return isinstance(other, Arg) and self.index == other.index

    def __hash__(self):
        return self.index

# This class represents an argument which was modified in an expression
# In particular, since arguments can be pointers, this allows to specify
# an argument (i.e., a pointer) + an offset
# NOTE: the only supported expressions for now are arg + offset
class Argument:
    def __init__(self, argument: Arg, offset: int):
        self.argument = argument
        self.offset = offset
    
    # Returns the offset from the argument
    def byte(self):
        return self.offset

    def __str__(self):
        return f"Argument({self.argument} + {self.byte()})"

    def expr(self):
        return self.argument.symbol + self.byte()

    def __eq__(self, other):
        if not isinstance(other, Argument): return False
        return self.argument == other.argument and self.byte() == other.byte()

    def __hash__(self):
        return hash((self.argument.__hash__(), self.offset))

# This represents a bit of an argument
class ArgumentBit(AbstractValue):
    def __init__(self, argument: Argument, bit: int, inverted: bool):
        self.argument = argument
        self.bit = bit
        self.inverted = inverted

    def get_bit_index(self):
        return self.argument.byte() * 8 + self.bit

    def is_inverted(self):
        return self.inverted

    def __str__(self):
        inv_str = '~' if self.inverted else ''
        return f"{inv_str}{self.argument}:{self.get_bit_index()}"

    def __eq__(self, other):
        if not isinstance(other, ArgumentBit): return False
        return self.argument == other.argument and \
                self.get_bit_index() == other.get_bit_index() and \
                self.is_inverted() == other.is_inverted()

    def __hash__(self):
        return hash((self.argument.__hash__(), self.bit, self.inverted))

    def complementary(self, other):
        if not isinstance(other, ArgumentBit): return False
        return self.argument == other.argument and \
                self.get_bit_index() == other.get_bit_index() and \
                self.is_inverted() != other.is_inverted()

# This represents the output of a gate
# i: an integer index to distinguish different outputs of a repeater
class GateOutput(AbstractValue):
    def __init__(self, wwg: WiredWeirdGate, inverted: bool, i: int):
        self.wwg = wwg
        self.inverted = inverted
        self.i = i

    def __str__(self):
        return f'{"~" if self.inverted else ""}o_0x{self.wwg.wg.start_addr:x}@0x{self.wwg.call_addr:x}'

    def is_inverted(self):
        return self.inverted

    def blif_repr(self):
        return f"gateout_{self.wwg.wg.start_addr}_{self.wwg.str_call_addr()}_{self.i}"
    
    def __eq__(self, other):
        # Two GateOutputs instances are equal if
        # 0. They are both GateOutputs
        equal = isinstance(other, GateOutput)
        # 1. The same gate produce them
        equal = equal and self.wwg == other.wwg
        # 2. The inverted flag is the same
        equal = equal and self.inverted == other.inverted
        # 3. and if they come from the same indexed output
        equal = equal and self.i == other.i
        return equal
    
    # This function checks if two GateOutputs can be complementary 
    # (i.e., one the opposite of the other)
    def complementary(self, other):
        if not isinstance(other, GateOutput): return False
        return self.wwg == other.wwg and \
                self.is_inverted() != other.is_inverted()

class FunctionOutput:
    def __init__(self, bigendian=False):
        self.outputs = {}
        self.bigendian = bigendian

    # Adds an output for an argument
    # arg: the Argument object "containing" the values
    # val_list: list of bit values from MSB to LSB
    def add(self, arg, val_list):
        self.outputs[arg] = val_list

    def get(self, arg):
        return self.outputs[arg]

    def iterator(self):
        return self.outputs.items()

    # Finds the value in the function output.
    # If found, the index of the argument and the corresponding bit is returned
    def find(self, value):
        for a in self.outputs:
            for i, o in enumerate(self.outputs[a][::-1]):
                if value == o:
                    return (a.index, i)
        return None
