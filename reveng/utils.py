import angr
import claripy
import capstone

def invert_map(m: dict):
    return {v: k for k, v in m.items()}

# expr: the target claripy expression
# target_name: name of the variable to search for in expr
def extract_bit_ranges(expr, target_name):
    bit_ranges = []

    # If this is an Extract operation
    if expr.op == 'Extract':
        high, low = expr.args[0], expr.args[1]
        inner = expr.args[2]
        if inner.op == 'BVS' and inner.args[0] == target_name:
            bit_ranges.append((high, low))

    # Recurse into arguments
    for arg in expr.args:
        if isinstance(arg, claripy.ast.Base):
            bit_ranges.extend(extract_bit_ranges(arg, target_name))

    return bit_ranges

# Returns the symbol with the specified name in expr
def extract_symbol_from_expression(expr, symbol_name: str):
    if not hasattr(expr, "args"): return None
    if not hasattr(expr, "op"): return None
    op = expr.op
    args = expr.args
    if op == "BVS" and args[0] == symbol_name:
        return expr
    else:
        results = tuple({r for a in args if (r := extract_symbol_from_expression(a, symbol_name)) is not None})
        assert len(results) <= 1
        return results[0] if len(results) == 1 else None

# This analyzes the assembly code starting at the given address, looking for a
# ret instruction and returns its address
def find_ret_instruction(proj: angr.Project, start_addr: int):
    while True:
        block = proj.factory.block(start_addr)
        if not block.capstone.insns: break
        for i in block.capstone.insns:
            if i.mnemonic == "ret":
                return i.address
        start_addr += (block.size if block.size else 1)
    return None
    
# This function returns the jump address(es) of the next call
def extract_call_address(state):
    block = state.project.factory.block(state.addr, num_inst=1)
    targets = block.vex.constant_jump_targets
    return tuple(targets)

# Returns the disassembly of the instruction pointed to by IP
def extract_current_instruction(state):
    instr = state.inspect.instruction
    # Get the disassembly of the current instruction
    disass = state.project.factory.block(instr, num_inst=1).capstone.insns[0]
    return disass

def get_instrs(state, num_instrs):
    instrs = []
    addr = state.inspect.instruction
    while True:
        block = state.project.factory.block(addr, num_inst=num_instrs - len(instrs))
        if not block.capstone.insns: break
        instrs.extend(block.capstone.insns)
        addr += (block.size if block.size else 1)
    return instrs
