import angr
import capstone
import claripy
from capstone.x86 import *

from utils import invert_map

# Computes a claripy expression of a memory expression from a capstone operation
def compute_memory_expression(m: capstone.x86.X86Op, state: angr.SimState):
    # Get the value of registers
    mapping = register_capstone_mapping()
    base = mapping[m.mem.base] if m.mem.base != 0 else None
    index = mapping[m.mem.index] if m.mem.index != 0 else None
    scale = m.mem.scale
    displacement = m.mem.disp
    assert (base is None or hasattr(state.regs, base)) \
            and (index is None or hasattr(state.regs, index)),  f'Register {base} or {index} not in state'
    vbase = getattr(state.regs, base) if base is not None else 0
    vindex = getattr(state.regs, index) if index is not None else 0
    return vbase + scale * vindex + displacement

# Returns a map between a register name (angr) and a symbol for that register
def get_symbolic_register_representation():
    reg_list = register_capstone_mapping().values()
    symb = {}
    for r in reg_list:
        symb[r] = claripy.BVS(f"sym_{r}", 64)
    return symb

def get_capstone_mapping_register(capstone_reg: int):
    mapping = register_capstone_mapping()
    assert capstone_reg in mapping, f"{capstone_reg}: unrecognized register"
    return mapping[capstone_reg]

def get_register_capstone_mapping(reg: str):
    mapping = invert_map(register_capstone_mapping())
    assert reg in mapping, f"{reg}: unrecognized register"
    return mapping[reg]

def register_capstone_mapping():
    mapping = {
            X86_REG_AH: 'ah',
            X86_REG_AL: 'al',
            X86_REG_AX: 'ax',
            X86_REG_BH: 'bh',
            X86_REG_BL: 'bl',
            X86_REG_BP: 'bp',
            X86_REG_BPL: 'bpl',
            X86_REG_BX: 'bx',
            X86_REG_CH: 'ch',
            X86_REG_CL: 'cl',
            X86_REG_CX: 'cx',
            X86_REG_DH: 'dh',
            X86_REG_DI: 'di',
            X86_REG_DIL: 'dil',
            X86_REG_DL: 'dl',
            X86_REG_DX: 'dx',
            X86_REG_EAX: 'eax',
            X86_REG_EBP: 'ebp',
            X86_REG_EBX: 'ebx',
            X86_REG_ECX: 'ecx',
            X86_REG_EDI: 'edi',
            X86_REG_EDX: 'edx',
            X86_REG_EFLAGS: 'eflags',
            X86_REG_EIP: 'eip',
            X86_REG_ESI: 'esi',
            X86_REG_ESP: 'esp',
            X86_REG_IP: 'ip',
            X86_REG_RAX: 'rax',
            X86_REG_RBP: 'rbp',
            X86_REG_RBX: 'rbx',
            X86_REG_RCX: 'rcx',
            X86_REG_RDI: 'rdi',
            X86_REG_RDX: 'rdx',
            X86_REG_RIP: 'rip',
            X86_REG_RSI: 'rsi',
            X86_REG_RSP: 'rsp',
            X86_REG_SI: 'si',
            X86_REG_SIL: 'sil',
            X86_REG_SP: 'sp',
            X86_REG_SPL: 'spl',
            X86_REG_R8: 'r8',
            X86_REG_R9: 'r9',
            X86_REG_R10: 'r10',
            X86_REG_R11: 'r11',
            X86_REG_R12: 'r12',
            X86_REG_R13: 'r13',
            X86_REG_R14: 'r14',
            X86_REG_R15: 'r15',
            X86_REG_R8B: 'r8b',
            X86_REG_R9B: 'r9b',
            X86_REG_R10B: 'r10b',
            X86_REG_R11B: 'r11b',
            X86_REG_R12B: 'r12b',
            X86_REG_R13B: 'r13b',
            X86_REG_R14B: 'r14b',
            X86_REG_R15B: 'r15b',
            X86_REG_R8D: 'r8d',
            X86_REG_R9D: 'r9d',
            X86_REG_R10D: 'r10d',
            X86_REG_R11D: 'r11d',
            X86_REG_R12D: 'r12d',
            X86_REG_R13D: 'r13d',
            X86_REG_R14D: 'r14d',
            X86_REG_R15D: 'r15d',
            X86_REG_R8W: 'r8w',
            X86_REG_R9W: 'r9w',
            X86_REG_R10W: 'r10w',
            X86_REG_R11W: 'r11w',
            X86_REG_R12W: 'r12w',
            X86_REG_R13W: 'r13w',
            X86_REG_R14W: 'r14w',
            X86_REG_R15W: 'r15w',
    }
    return mapping

def get_canonical_register(capstone_reg: int):
    mapping = get_canonical_mapping()
    assert capstone_reg in mapping, f'{capstone_reg}: unrecognized register'
    return mapping[capstone_reg]

def get_canonical_mapping():
    mapping = {}
    mapping[X86_REG_AH]   = X86_REG_RAX
    mapping[X86_REG_AL]   = X86_REG_RAX
    mapping[X86_REG_AX]   = X86_REG_RAX
    mapping[X86_REG_EAX]  = X86_REG_RAX
    mapping[X86_REG_RAX]  = X86_REG_RAX

    mapping[X86_REG_BH]   = X86_REG_RBX
    mapping[X86_REG_BL]   = X86_REG_RBX
    mapping[X86_REG_BX]   = X86_REG_RBX
    mapping[X86_REG_EBX]  = X86_REG_RBX
    mapping[X86_REG_RBX]  = X86_REG_RBX

    mapping[X86_REG_CH]   = X86_REG_RCX
    mapping[X86_REG_CL]   = X86_REG_RCX
    mapping[X86_REG_CX]   = X86_REG_RCX
    mapping[X86_REG_ECX]  = X86_REG_RCX
    mapping[X86_REG_RCX]  = X86_REG_RCX

    mapping[X86_REG_DH]   = X86_REG_RDX
    mapping[X86_REG_DL]   = X86_REG_RDX
    mapping[X86_REG_DX]   = X86_REG_RDX
    mapping[X86_REG_EDX]  = X86_REG_RDX
    mapping[X86_REG_RDX]  = X86_REG_RDX

    mapping[X86_REG_DIL]  = X86_REG_RDI
    mapping[X86_REG_DI]   = X86_REG_RDI
    mapping[X86_REG_EDI]  = X86_REG_RDI
    mapping[X86_REG_RDI]  = X86_REG_RDI

    mapping[X86_REG_SIL]  = X86_REG_RSI
    mapping[X86_REG_SI]   = X86_REG_RSI
    mapping[X86_REG_ESI]  = X86_REG_RSI
    mapping[X86_REG_RSI]  = X86_REG_RSI

    mapping[X86_REG_R8B]  = X86_REG_R8
    mapping[X86_REG_R8W]  = X86_REG_R8
    mapping[X86_REG_R8D]  = X86_REG_R8
    mapping[X86_REG_R8]   = X86_REG_R8

    mapping[X86_REG_R9B]  = X86_REG_R9
    mapping[X86_REG_R9W]  = X86_REG_R9
    mapping[X86_REG_R9D]  = X86_REG_R9
    mapping[X86_REG_R9]   = X86_REG_R9

    mapping[X86_REG_R10B] = X86_REG_R10
    mapping[X86_REG_R10W] = X86_REG_R10
    mapping[X86_REG_R10D] = X86_REG_R10
    mapping[X86_REG_R10]  = X86_REG_R10

    mapping[X86_REG_R11B] = X86_REG_R11
    mapping[X86_REG_R11W] = X86_REG_R11
    mapping[X86_REG_R11D] = X86_REG_R11
    mapping[X86_REG_R11]  = X86_REG_R11

    mapping[X86_REG_R12B] = X86_REG_R12
    mapping[X86_REG_R12W] = X86_REG_R12
    mapping[X86_REG_R12D] = X86_REG_R12
    mapping[X86_REG_R12]  = X86_REG_R12

    mapping[X86_REG_R13B] = X86_REG_R13
    mapping[X86_REG_R13W] = X86_REG_R13
    mapping[X86_REG_R13D] = X86_REG_R13
    mapping[X86_REG_R13]  = X86_REG_R13

    mapping[X86_REG_R14B] = X86_REG_R14
    mapping[X86_REG_R14W] = X86_REG_R14
    mapping[X86_REG_R14D] = X86_REG_R14
    mapping[X86_REG_R14]  = X86_REG_R14

    mapping[X86_REG_R15B] = X86_REG_R15
    mapping[X86_REG_R15W] = X86_REG_R15
    mapping[X86_REG_R15D] = X86_REG_R15
    mapping[X86_REG_R15]  = X86_REG_R15
