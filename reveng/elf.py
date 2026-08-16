import os
import sys
import time
from collections import defaultdict
from itertools import dropwhile, combinations

import angr
import capstone

import wr
import asm
import utils
import weirdgate
import uarch
import preprocessing
from hooks import *
from values import *

class WeirdGateFoundException(Exception):
    # address: address following the call to mod_ret_addr
    # call_address: address of the call to mod_ret_addr
    # state: state before calling mod_ret_addr
    # cont: state after the execution and return of mod_ret_addr
    # delta: jump performed by mod_ret_addr
    def __init__(self, address, call_address, state, cont, delta):
        super().__init__()
        self.address = address
        self.call_address = call_address
        self.state  = state.copy()
        self.cont = cont
        self.delta = delta

class ELF:
    def __init__(self, elf_path):
        self.elf_path = elf_path
        assert os.path.isfile(elf_path), f"{elf_path}: not a valid ELF file"
        # auto_load_libs is set to True so that Rand can work
        self.angr_proj = angr.Project(elf_path, auto_load_libs=True, use_sim_procedures=False)
        self.preprocessor = preprocessing.ELF_Preprocessor(elf_path)

    # Returns a dictionary that associates a memory address to a symbol in the binary
    # NOTE: 0xELF works also on stripped binaries; this function is here only for debugging purposes
    def get_symbol_table(self):
        if not hasattr(self, "symbol_table"):
            symbols = list(self.angr_proj.loader.main_object.symbols)
            self.symbol_table = {s.name: s.rebased_addr for s in symbols}
        return self.symbol_table

    def build_weird_function(self, address: int, arguments: int):
        return WeirdFunction(address, arguments, self)

    def disass_all(self):
        if not hasattr(self, "asm_instructions"):
            text_section = [s for s in self.angr_proj.loader.main_object.sections.raw_list if s.name == ".text"][0]
            start = text_section.vaddr
            end = start + text_section.memsize
            annotated_asm_code = []
            symbol_table = self.get_symbol_table()

            curaddr = start
            while curaddr < end:
                block = self.angr_proj.factory.block(curaddr)
                raw_asm_code = block.capstone.insns
                annotated_asm_code += [i for i in raw_asm_code]

                curaddr += (block.size if block.size else 1)

            self.asm_instructions = annotated_asm_code

        return self.asm_instructions

# Represents a weird function in the analyzed binary
# address: the address the function starts at
# arguments: the number of arguments it takes (NOTE: this can be larger than
#            the actual number) 
# parser: the ELF instance that is parsing the current binary
class WeirdFunction:
    def __init__(self, address: int,  arguments: int, parser: ELF):
        self.address = address
        self.num_arguments = arguments
        self.parser = parser

        self.weird_registers = wr.WeirdRegisterCollection()
        self.weird_gates = weirdgate.WeirdGatesCollection()
        self.wiring = weirdgate.WiredWeirdGatesCollection()

        # Initialize the state for symbolic execution.
        self.args = {(s := f"arg{i:03}") : Arg(i, claripy.BVS(s, 64, explicit_name=True)) for i in range(self.num_arguments)}
        self.arguments = ArgumentsCollection(self.args)
        cc=angr.calling_conventions.SimCCSystemVAMD64(self.parser.angr_proj.arch)

        prototype = angr.sim_type.SimTypeFunction(
            [angr.sim_type.SimTypeLongLong()] * self.num_arguments,
            angr.sim_type.SimTypeBottom()
        )

        state = self.parser.angr_proj.factory.call_state(address, *(a.symbol for a in self.args.values()), prototype=prototype, cc=cc, add_options={angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY, angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS}, ret_addr=0xdeadbeef)
        self.ret_addr = 0xdeadbeef

        state.regs.rbp = state.regs.rsp
        state.regs.r15 = 0xdeadffffdeadffff
        state.regs.r14 = 0xdeadeeeedeadeeee
        state.regs.r13 = 0xdeaddddddeaddddd
        state.regs.r12 = 0xdeadccccdeadcccc
        state.regs.rbx = 0xdead2222dead2222
        
        self.dereference_tracker = ArgTracker()
        state.inspect.b('mem_read', when=angr.BP_AFTER, action=self.dereference_tracker.mem_access)

        state.memory.write_strategies = [SimConcretizationForWeirdRegisters()]

        self.argument_writes = {}

        self.angr_state = state

        # RSB emulation
        self.rsb = uarch.RSB()
        self.rsb_ret = False

        # I define timer as a function that takes a timestamp,
        # reads a memory address
        # takes another timestamp
        # Other actions may occur between the two timestamps, as long as no
        # memory reads are performed during that time 
        self.timer = wr.WeirdRegisterReader()
        self.timestamps = self.parser.preprocessor.find_timestamps(self.address)
        timestamp_lengths = {'rdtscp': 3, 'rdtsc': 2}
        for label in self.timestamps:
            for t in self.timestamps[label]:
                self.parser.angr_proj.hook(t, self.timer.rdtscx_hook, length=timestamp_lengths[label], replace=True)

        # The outputs of this weird function
        self.outputs = FunctionOutput()
    
    def __wr_argument_initialization(self, expr, reset=True):
        # The expression must have only one variable and it must be
        # associated with an argument
        variables = tuple(expr.variables)
        if not len(variables) == 1:
            return
        v = variables[0]
        symbol = utils.extract_symbol_from_expression(expr, v)
        if not symbol is not None:
            #f"No symbol named {v} in {expr}"
            return
        
        # Initialize the weird register that is flushed
        # We know that the flushed expression corresponds to the non-inverted
        # value when the argument bit is zero. Therefore, by setting the input
        # argument to zero we get the non-inverted weird register and by
        # setting it to 1 we get the inverted location
        lwrp = claripy.simplify(claripy.replace(expr, symbol, claripy.BVV(0, 64)))
        lwrn = claripy.simplify(claripy.replace(expr, symbol, claripy.BVV(-1, 64)))
        assert lwrp.concrete, lwrn.concrete
        wrp = self.weird_registers.add(lwrp.concrete_value)
        wrn = self.weird_registers.add(lwrn.concrete_value)

        # Extract the bit of the argument that has been used
        bits = utils.extract_bit_ranges(expr, v)
        if not len(bits) == 1:
            return
        extracted_bit = bits[0]
        if not extracted_bit[0] == extracted_bit[1]:
            return
        bit = extracted_bit[0]

        original_arg = self.dereference_tracker.find(symbol)
        argument = self.arguments.get(original_arg)

        vwrp = ArgumentBit(argument, bit, False if reset else True)
        vwrn = ArgumentBit(argument, bit, True if reset else False)
        wrp.set_value(vwrp)
        wrn.set_value(vwrn)
        
    # This function creates a new weird register that either contains an
    # argument or an output for a gate
    def __parse_wr_init(self, flushed_expr, reset=True, conditions=[]):
        if flushed_expr.symbolic:
            # Since I only use symbols for arguments 
            # (at least during the circuit phase)
            # this must be the initialization of an argument
            
            self.__wr_argument_initialization(flushed_expr, reset=reset)
        else:
            # NOTE: this is a concrete expression, but it does not mean that I 
            #       am not initializing an argument it depends if we are in a conditional branch or not
            # Check if we are in a conditional branch
            if conditions is not None:
                cond = conditions
                # Now I check if the expression contains an argument and I extract the variable and the bit range
                vs = tuple(cond.variables)
                assert len(vs) == 1, "Argument initialization can be dependent only on one variable"
                v = vs[0]
                symbol = utils.extract_symbol_from_expression(cond, v)
                bits = utils.extract_bit_ranges(cond, v)
                assert len(bits) == 1, f"Unrecognized expression for clflush ({cond})"
                extracted_bit = bits[0]
                assert extracted_bit[0] == extracted_bit[1]
                bit = extracted_bit[0]
                original_arg = self.dereference_tracker.find(symbol)
                argument = self.arguments.get(original_arg)

                # Now condition can be equivalent to bit == 0 or not.
                sample_cond = (symbol[bit] == 0)
                s = claripy.Solver()
                is_zero = s.satisfiable(extra_constraints=[cond, sample_cond])
                negated = is_zero ^ reset
                wr_value = ArgumentBit(argument, bit, negated)
            else: 
                wr_value = Value(0 if reset else 1)
            # This is a concrete expression, therefore I can use the value as
            # the location of the weird register and the value will be just
            # zero
            # NOTE: at this point I don't know anything about its dual or if
            # this is negated or not
            wr = self.weird_registers.add(flushed_expr.concrete_value)
            if wr.get_value() is None or isinstance(wr.get_value(), Value):
                wr.set_value(wr_value)

    def __instr_break(self, state):
        # 2 instructions: the current one and the next one in the binary, not counting jumps or calls
        disass = utils.get_instrs(state, 2)
        mnemonic = disass[0].insn.mnemonic 
        if mnemonic == "clflush":
            # Extract the memory address that is flushed
            if not len(disass[0].operands) >= 1: return
            o = disass[0].operands[0]
            if not o.type == capstone.CS_OP_MEM: return
            expr = asm.compute_memory_expression(o, state)
            self.__parse_wr_init(expr, reset=True, conditions=state.globals.get('last_branch'))
        elif mnemonic == "call":
            targets = utils.extract_call_address(state)

            if len(targets) == 1:
                destination = targets[0]
                self.rsb.call(disass[0].insn.address, None, disass[1].insn.address, state.copy())
            else:
                raise Exception("Symbolic call")

        # If this is a `ret`, I have to check if the return address is the one
        # that I was expecting. If not, I have just executed mod_ret_addr
        # Therefore, I need to stop because I now know _one_ mod_ret_addr place
        # and I can use the state stack to go back to the state that I saved
        # _before_ calling this mod_ret_addr. I use the state in order to build
        # the weird gate and then continue the execution
        elif mnemonic == "ret":
            self.rsb_ret = True
        # NOTE: This "trick" is performed in case of hooked function (we intercept
        #      the call, but not the ret for those)
        #      Therefore, we analyze if the RSB is empty, if it is not but the
        #      return address is the one of the current function, it means that we
        #      called something that was supposed to return here, so we pop the
        #      entry and even if we do all the checks they will not detect anything
        #
        elif not self.rsb.is_empty() and self.rsb.peek().ret_addr == disass[0].insn.address:
            self.rsb.ret()
        elif mnemonic == "rdtscp" or mnemonic == "rdtsc":
            self.timer.record_instr()
    
    def __instr_break_after(self, state):
        if self.rsb_ret:
            self.rsb_ret = False
            rsb_entry = self.rsb.ret()
            delta = state.solver.eval(state.regs.ip) - rsb_entry.ret_addr
            if delta != 0:
                ga = rsb_entry.at_addr
                ra = rsb_entry.ret_addr
                s = rsb_entry.state
                raise WeirdGateFoundException(ra, ga, s, state.copy(), delta)
        elif self.timer.is_instr_recorded():
            self.timer.timer(state)

    def __memwrite_after(self, state):
        addr = state.inspect.mem_write_address
        expr = state.inspect.mem_write_expr
        
        # I need to track memory writes for outputs only after the first timer call
        if self.timer.has_timer_started():
            if addr.symbolic:
                self.argument_writes[addr] = expr
        self.__parse_wr_init(addr, reset=False, conditions=state.globals.get('last_branch'))

    def __memread_before(self, state):
        addr = state.inspect.mem_read_address

        if addr.concrete:
            conc_addr = addr.concrete_value
            if (wr := self.weird_registers.find(conc_addr)) is not None:
                if self.timer.record_memaccess_conditional(state.inspect.mem_read_address.concrete_value):
                    return
        self.__parse_wr_init(addr, reset=False, conditions=state.globals.get('last_branch'))
                
    def get_last_jump_guard(self, jump_guards):
        jump_guards = [x for x in jump_guards if not x.is_true() or x.is_false()]
        return [jump_guards[-1]] if len(jump_guards) > 0 else []

    def __exit(self, state):
        eg = state.inspect.exit_guard  
        if eg is not None and getattr(eg, "symbolic", False) and not eg.is_true() and not eg.is_false():
            state.globals["last_branch"] = state.inspect.exit_guard

    # Extracts all the weird gates and registers in the binary, including the wiring
    def parse(self):
        start = time.time()
        simgr = self.parser.angr_proj.factory.simulation_manager(self.angr_state)

        self.angr_state.inspect.b('instruction', when=angr.BP_BEFORE, action=self.__instr_break)
        self.angr_state.inspect.b('instruction', when=angr.BP_AFTER, action=self.__instr_break_after)
        self.angr_state.inspect.b('mem_write', when=angr.BP_AFTER, action=self.__memwrite_after)
        self.angr_state.inspect.b('mem_read', when=angr.BP_BEFORE, action=self.__memread_before)
        self.angr_state.inspect.b('exit', when=angr.BP_AFTER, action=self.__exit)

        # Get address of ret instruction
        end = utils.find_ret_instruction(self.parser.angr_proj, self.address)
        self.rsb.call(0,0,self.ret_addr,self.angr_state.copy())
        simgr.stashes['paused'] = []

        while True:
            try:
                # Before stepping, I check if there is more than one active state
                if len(simgr.stashes['active']) > 1 or len(simgr.stashes['paused']) > 0:
                    # Find the minimum IP in all the states
                    states = simgr.stashes['active'] + simgr.stashes['paused']
                    min_ip = states[0].regs.ip
                    min_state = states[0]
                    for s in states:
                        if claripy.is_true(s.regs.ip < min_ip):
                            min_ip = s.regs.ip
                            min_state = s
                    simgr.stashes['active'] = [min_state]
                    states.remove(min_state)
                    simgr.stashes['paused'] = states

                simgr.step(opt_level=0, extra_stop_points=[e for l in self.timestamps for e in self.timestamps[l]])
                simgr.move(from_stash="active", to_stash="finished", filter_func=lambda s: s.addr == self.ret_addr)
                # Iterate through all active stashes if needed: merge the ones with same IP
                states = simgr.stashes['active'] + simgr.stashes['paused']
                if len(states) > 1:
                    # Merge
                    while True:
                        did_one_merge = False

                        for s1, s2 in combinations(states, 2):
                            if s1.addr != s2.addr:
                                continue
                            if s1.callstack != s2.callstack:
                                continue

                            merged, _, did_merge = s1.merge(s2)

                            if did_merge:
                                did_one_merge = True
                                states.remove(s1)
                                states.remove(s2)

                                merged.globals.pop('last_branch', None)

                                states.append(merged)
                                break
                        if not did_one_merge: break
                    simgr.stashes['active'] = states
                    simgr.stashes['paused'] = []
                if simgr.finished:
                    break
            except WeirdGateFoundException as e:
                try:
                    call_address = self.rsb.rsb[-1][0]
                except:
                    call_address = 0
                sys.stderr.write(f"[{time.time() - start:.03f}] Found gate defined at 0x{e.address:x} called at 0x{call_address:x}\n")
                wg = self.weird_gates.add(self.parser, e.address, e.delta)
                self.wiring.add(wg, tuple(self.rsb.rsb), e.state, self.weird_registers)
                simgr = self.parser.angr_proj.factory.simulation_manager(e.cont)

        # Now I have a list of all the arguments used as address for writing
        # things as well as the value written to that address

        # Get the arguments used for output and sort them by index (i.e., order
        # in which they should be defined in the function) and then by offset
        # so that we get
        # e.g., arg2 + 8, arg2 + 7, arg2 + 6, ..., arg2 + 1, arg2 + 0, arg3 + 1, arg3 + 0 and so on
        arch_bits = self.parser.angr_proj.arch.bits
        arguments_for_output = [self.arguments.get(x) for x in self.argument_writes.keys()]
        arguments_for_output = sorted(arguments_for_output, key= \
                lambda x: ( \
                    (x.argument.index << arch_bits) + (1<<arch_bits - x.offset) \
                ))
        assert len(arguments_for_output) > 0, f"This circuit seems not to write an output. This is odd"
        unique_arguments = {a.argument for a in arguments_for_output}

        for ua in unique_arguments:
            # For each found argument, we build a list of bit values, from MSB to LSB
            bit_values = []
            for a in arguments_for_output:
                if a.argument == ua:
                    # Extract the expression from argument_writes
                    exprs = [self.argument_writes[k] for k in self.argument_writes.keys() \
                                if claripy.is_true(k == a.expr())]
                    assert len(exprs) == 1
                    expr = exprs[0]
                    # Iterate through all the bits of the value from MSB to LSB
                    for b in range(7, -1, -1):
                        bit = expr[b]
                        if bit.symbolic:
                            symbols = tuple(bit.variables)
                            # This bit is computed from an expression of type
                            # if (end_ts - start_ts) <= K then 1 else 0
                            # or something like that, so I have two symbols
                            if len(symbols) == 2:
                                sym1 = utils.extract_symbol_from_expression(bit, symbols[0])
                                sym2 = utils.extract_symbol_from_expression(bit, symbols[1])
                                if (wr := self.timer.find((sym1, sym2))) is not None:
                                    wr = self.weird_registers.find(wr)
                                    bit_values.append(wr.get_value())
                            elif len(symbols) == 1:    # This could be an argument reported directly in an output
                                sym = utils.extract_symbol_from_expression(bit, symbols[0])
                                original_arg = self.dereference_tracker.find(sym)
                                if (argbit := self.arguments.get(original_arg, do_not_add=True)) is not None:
                                    bits = utils.extract_bit_ranges(bit, symbols[0])
                                    assert len(bits) == 1
                                    bs, be = bits[0]
                                    assert bs == be
                                    bit_values.append(ArgumentBit(argbit, be, False))
                            else:    # This MUST be the error correction!
                                bit_values = []
                                break
                        else:
                            bit_values.append(bit.concrete_value)
            if len(bit_values) > 0:
                self.outputs.add(ua, bit_values)

        # The final task is to iterate for all the gates and find possible gates that have no dual set.
        # This can happen if the output of a repeater goes directly to the
        # output without being connected to another gate
        self.wiring.fix_duals()
        
        # At the end of this function, we have weird gates (self.weird_gates)
        # the wiring (self.wiring) and the outputs (self.outputs) of the circuit
        return

    def scan_wrs_for_inputs(self):
        inputs = set()
        for wr in self.weird_registers.iterator():
            v = wr.get_value()
            if v is not None and isinstance(v, ArgumentBit):
                inputs.add(v)
        
        # This is just for convenience and not useful for OxELF
        arch_bits = self.parser.angr_proj.arch.bits
        inputs = sorted(inputs, key=lambda x: (x.argument.argument.index << arch_bits) + ((1<<arch_bits) - x.get_bit_index()))
        return inputs
    
    def blif(self, iz=True):
        inputs = self.scan_wrs_for_inputs()
        outputs = self.outputs
        wiring = self.wiring

        def get_blif_name(val):
            if isinstance(val, ArgumentBit):
                return f'_in{val.argument.argument.index}[{val.get_bit_index()}]'
            elif isinstance(val, GateOutput):
                return val.blif_repr()
            elif isinstance(val, Value):
                assert val.value == 0 or val.value == 1
                return '$false' if val.value == 0 else '$true'
            elif isinstance(val, int):
                assert val == 0 or val == 1
                return '$false' if val == 0 else '$true'

        def get_blif_output_name(index, bit):
            return f'_out{index}[{bit}]'

        blif_model_string = '.model OxELF_output'
        blif_input_string = '.inputs ' + ' '.join([get_blif_name(i) for i in inputs if i.is_inverted() == False])
        if iz:
            blif_output_string = '.outputs ' + ' '.join([get_blif_output_name(a.index, i)
                                                     for a, ol in outputs.iterator() for i, o in enumerate(dropwhile(lambda x: x==0, ol))])
        else:
            blif_output_string = '.outputs ' + ' '.join([get_blif_output_name(a.index, i) for a, ol in outputs.iterator() for i, o in enumerate(ol)])

        blif_constants = '.names $false\n.names $true\n1\n.names $undef'
        blif_gates = ''
        blif_end = '.end'


        # First thing's first, I want to iterate through the outputs of the circuit.
        # Some outputs could be classified as "inverted".
        # For such outputs, I want to find the gate that produce them and flag it for inversion
        # When we will print the gate, if it is flagged, we have to print the opposite LUT.
        # Dictionary of gate call index -> what part of the gate to print
        # (1: non-inverted, 2: inverted, 3: both)
        # I print out the non-inverted part by default
        # 
        handle_dual_gate_wiring = {c.call_addr: 1 for c in self.wiring.iterator()}

        # I want to identify the repeaters whose output wires are both outputs of the circuit
        # and used in the inner circuit
        # Therefore, I build a list of all the outputs.
        # I use a dictionary so that access is easier
        all_outputs = {}
        # I iterate through all the outputs and mark the gates for which this output is inverted as such
        for a, out in outputs.iterator():
            for o in out:
                if isinstance(o, GateOutput):
                    all_outputs[id(o)] = o
                    if o.is_inverted():
                        handle_dual_gate_wiring[o.wwg.call_addr] = 2
            
        for w in wiring.iterator():
            if w.wg.is_gate_repeater() and handle_dual_gate_wiring[w.call_addr] == 2:
                # Iterate through its outputs and see if there are output that are not
                # We iterate through only non-inverted registers and then consider even the dual
                oRs = w.get_outputs(inverted=False)
                for oR in oRs:
                    doR = oR.get_dual()
                    v = oR.get_value()
                    dv = doR.get_value()
                    if not (id(v) in all_outputs or id(dv) in all_outputs):
                        # This means at least one output is used in another gate
                        handle_dual_gate_wiring[w.call_addr] = 3
                        break

        performed_outputs = []
        for wwg in wiring.iterator():
            inverted = []
            if (handle_dual_gate_wiring[wwg.call_addr] & 0x1 != 0):
                inverted.append(False)
            if (handle_dual_gate_wiring[wwg.call_addr] & 0x2 != 0):
                inverted.append(True)

            for inv in inverted:
                non_inverted_outputs = wwg.get_outputs(inv)
                truth_tables = wwg.get_truth_tables(inv)
                # If we have more than one non-inverted output, we output a number
                # of gates equal to the number of non-inverted outputs

                for nio in non_inverted_outputs:
                    # 1. Print the header for this gate
                    gate_header = f"# 0x{w.wg.start_addr:x}@{w.str_call_addr()}\n.names "
                    tt = truth_tables[nio]
                    header, values = tt.compute()
                    for r in header:
                        v = r.get_value()
                        gate_header += get_blif_name(v) + ' '

                    O = outputs.find(nio.get_value())
                    if O is None:
                        assert isinstance(nio.get_value(), GateOutput)
                        gate_header += nio.get_value().blif_repr()
                    else:
                        gate_header += get_blif_output_name(O[0], O[1])
                        performed_outputs.append(O)

                    gate_header += '\n'

                    gate_body = ""
                    for i in values:
                        result = values[i]

                        if result == 1:
                            gate_body += f"{''.join([str(x) for x in list(i)])} {result}\n"

                    blif_gates += gate_header + gate_body
        
        for arg, ol in outputs.iterator():
            ai = arg.index
            # Identify index of first non-zero bit of this argument
            last_nonzero = None
            for i, o in enumerate(ol[::-1]):
                if o != 0:
                    last_nonzero = i

            for i, o in enumerate(ol[::-1]):
                if i > last_nonzero and iz: break
                if (ai, i) not in performed_outputs:
                    # Add the output to the blif file
                    gate = '.names '
                    if o == 0:
                        gate += f'$false {get_blif_output_name(ai, i)}\n1 1\n'
                    elif o == 1:
                        gate += f'$true {get_blif_output_name(ai, i)}\n1 1\n'
                    elif isinstance(o, ArgumentBit):
                        gate += f'{get_blif_name(o)} {get_blif_output_name(ai, i)}\n1 1\n'
                    else:
                        raise Exception("Unexpected value for output")
                    blif_gates += gate
    
        return blif_model_string        + '\n' \
                + blif_input_string     + '\n' \
                + blif_output_string    + '\n' \
                + blif_constants        + '\n' \
                + blif_gates            \
                + blif_end
