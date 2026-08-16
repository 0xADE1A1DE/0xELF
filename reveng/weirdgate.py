import time
from typing import List
from collections import defaultdict

import angr
import claripy
import capstone

from angr.concretization_strategies.base import SimConcretizationStrategy

import wr
import asm
import rand
import utils
import values
from dnf import DNF, TruthTable

# Represents a RAW Forest
# Read-After-Write dependencies are stored here in the form of a dictionary: a
# node is identified by the address of an instruction (int) and the edges going
# out from a node I to nodes A1, A2, ..., AN (i.e., I depends on A1,...,AN) is
# encoded as an entry in the dictionary having the address of I as the key and,
# as the associated value, there is the list of the addresses of instructions
# A1,...,AN.
class RAWForest:
    def __init__(self):
        self.forest = defaultdict(list)

    # Asserts that instruction at address i depends on instruction at address d
    def assert_dependency(self, i: int, d: int):
        self.forest[i].append(d)
    
    # Returns the dependencies of instruction at address i
    def get_dependencies(self, i: int):
        if i in self.forest:
            return self.forest[i]
        return []

    # Returns the roots of the forest
    # i.e., the nodes that are not children of another node
    def roots(self, memory=None):
        if memory is None:
            return [n for n in self.forest if not any([n in C for C in self.forest.values()])]
        else:
            return [n for n in self.forest \
                    if not any([n in [x for x in C if x in memory] for C in self.forest.values()]) \
                    and n in memory]

    # Returns a list of nodes reachable from node N
    def reach(self, N: int):
        if not N in self.forest: return []
        w = []
        for n in self.forest[N]:
            w.append(n)
            w.extend(self.reach(n))
        return w
    
    # collapse is a function that is dependent on a list of instructions that
    # do memory reads. Therefore, we need a list of functions that do memory
    # reads in the gate.
    def collapse(self, memory_reading_instructions):
        roots = self.roots(memory_reading_instructions)
        self.forest = {r : self.reach(r) for r in roots}
        addresses = sorted(self.forest.keys())
        for a in addresses:
            if not a in memory_reading_instructions:
                self.forest.pop(a)
            else:
                self.forest[a] = [n for n in self.forest[a] if n in memory_reading_instructions]

class GateStateTracker:
    def __init__(self, parser):
        # Mapping between instruction address and state after
        # instruction (see above for the reason for which this is a
        # dictionary of lists
        self.instrs = defaultdict(list)
        self.memreads = defaultdict(list)
        self.memwrites = defaultdict(list)
        self.regreads = defaultdict(list)
        self.regwrites = defaultdict(list)
        self.record = True    # NOTE: this stays True and can be removed
        self.parser = parser
        arch = self.parser.angr_proj.arch
        self._gpr_offsets = {
            reg.vex_offset
            for reg in arch.register_list
            if reg.general_purpose
            and reg.vex_offset is not None
            and reg.vex_offset != arch.ip_offset
        }

    def record_instr(self, state):
        targets = utils.extract_call_address(state)
        if self.record:
            self.instrs[state.inspect.instruction] \
                    .append({r : getattr(state.regs, r) for r in state.arch.default_symbolic_registers})

    def record_memread(self, state):
        if self.record:
            self.memreads[state.inspect.instruction] \
                    .append(state.inspect.mem_read_address)

    def record_memwrite(self, state):
        if self.record:
            self.memwrites[state.inspect.instruction] \
                    .append(state.inspect.mem_write_address)

    def record_regread(self, state):
        if self.record:
            self.regreads[state.inspect.instruction] \
                    .append(state.inspect.reg_read_offset)

    def record_regwrite(self, state):
        if self.record:
            self.regwrites[state.inspect.instruction] \
                    .append(state.inspect.reg_write_offset)
    
    def get_instruction_addresses(self):
        return tuple(self.instrs.keys())

    def get_read_registers(self, addr: int):
        # NOTE: the registers that are actually read have their
        # ID number stored as a (concrete) BV.
        if not addr in self.regreads: return []
        return [v for x in self.regreads[addr] if isinstance(x, claripy.ast.bv.BV) \
                and x.concrete and (v := x.concrete_value) in self._gpr_offsets]

    def get_written_registers(self, addr: int):
        if not addr in self.regwrites: return []
        return [v for x in self.regwrites[addr] if isinstance(x, claripy.ast.bv.BV) \
                and x.concrete and (v := x.concrete_value) in self._gpr_offsets]

    def get_read_memaddresses(self, addr: int):
        if not addr in self.memreads: return []
        return self.memreads[addr]

    def get_written_memaddresses(self, addr: int):
        if not addr in self.memwrites: return []
        return self.memwrites[addr]
    
    # NOTE: we assume that read/writes in memory are not used for enforcing a
    # specific ordering on the instructions, instead, that both can be used to
    # set a weird register
    def get_memaddresses(self, addr: int):
        return self.get_read_memaddresses(addr) + self.get_written_memaddresses(addr)

    def get_raw_forest(self):
        forest = RAWForest()
        addresses = self.get_instruction_addresses()
        ordered_addresses = sorted(addresses)

        last_writer = {}

        for i in ordered_addresses:
            # Deduplicate
            for reg in set(self.get_read_registers(i)):
                j = last_writer.get(reg)
                if j is not None:
                    forest.assert_dependency(i, j)

            # Update the most recent writer for each register
            for reg in self.get_written_registers(i):
                last_writer[reg] = i

        return forest

class ConcretizationForMemoryReadsInGates(SimConcretizationStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _concretize(self, memory, addr, **kwargs):
        return [0]    # All memory reads return 0 nonetheless and it's faster this way

# This class represents a weird gate
# address: the starting address for the gate
# project: an angr project that loaded the binary in which the gate is present
# start_addr: the starting address of the transient part of the gate
# delta: the final instruction of the gate is at start_addr + delta
# name: an optional name for the gate
class WeirdGate:
    def __init__(self, parser: angr.project.Project,
                 start_addr: int, delta: int, name=None):
        self.parser = parser
        self.proj = parser.angr_proj
        self.start_addr = start_addr
        self.delta = delta

        self.name = name

        # Arbitrary assignment for handling the dual encoding
        # This must be the same for all gates
        self.assignment = rand.get_assignment()
        self.symbolic_registers = {}

        self.cache_register_location = {}

        self.__reverse()
        self.__handle_dual_encoding()

    def __track_behavior(self):
        if hasattr(self, "GST"): return self.GST

        # Initialize the state:
        # 1. Create a blank state
        # 2. Set general purpose registers to be symbols
        # 3. Restore Instruction Pointer and Stack Pointer to be concrete
        state = self.proj.factory.blank_state(addr=self.start_addr)
        for r in state.arch.default_symbolic_registers:
            bits = state.arch.registers[r][1] * 8
            symbol = claripy.BVS(f'sym_{r}', bits)
            setattr(state.regs, r, symbol)
            self.symbolic_registers[r] = symbol
        state.regs.ip = self.start_addr
        state.regs.sp = state.arch.initial_sp
        
        # Create breakpoints to track instructions, memory reads/writes and
        # register reads/writes
        self.GST = GateStateTracker(self.parser)
        state.inspect.b('instruction', when=angr.BP_BEFORE, action=self.GST.record_instr)
        state.inspect.b('mem_read', when=angr.BP_BEFORE, action=self.GST.record_memread)
        state.inspect.b('mem_write', when=angr.BP_BEFORE, action=self.GST.record_memwrite)
        state.inspect.b('reg_read', when=angr.BP_BEFORE, action=self.GST.record_regread)
        state.inspect.b('reg_write', when=angr.BP_BEFORE, action=self.GST.record_regwrite)

        # Assume memory reads return zero unless written
        # This is in line to what Flexo uses for bringing a weird register into
        # the cache
        state.options.add(angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY)

        # Since we assume that memory reads return zero, then the address we
        # read from is moot
        state.memory.read_strategies = [ConcretizationForMemoryReadsInGates()]

        # Initialize the simulation manager and symbolically execute the gate
        # opt_level=0 is necessary for the breakpoints to work correctly
        simgr = self.proj.factory.simulation_manager(state)
        end = self.start_addr + self.delta
        simgr.explore(find=end, opt_level=0)

        return self.GST

    def get_input_locations(self):
        if not hasattr(self, "register_locations"): self.get_dnfs()
        return [l for l in self.register_locations if l.is_input()]

    def get_output_locations(self):
        if not hasattr(self, "register_locations"): self.get_dnfs()
        return [l for l in self.register_locations if l.is_output()]

    def is_gate_repeater(self):
        if not hasattr(self, "is_repeater"):
            # 1. If the gate is a repeater, it will have more than two outputs
            #    and only two inputs
            inputs = self.get_input_locations()
            outputs = self.get_output_locations()
            if len(inputs) != 2 or len(outputs) == 2:
                self.is_repeater = False
            else:
                # 2. If the gate is a repeater, each output will copy an input
                #    i.e, each DNF is an identity
                self.is_repeater = all(dnf.is_identity() for dnf in self.get_dnfs().values())
        return self.is_repeater

    def __handle_dual_encoding(self):
        # Check if the gate is a repeater or not
        inputs = self.get_input_locations()
        outputs = self.get_output_locations()
        if self.is_gate_repeater():
            # Inputs have different inverted value
            assert len(inputs) == 2, f"Weird gate {self.name}@{self.start_addr}" \
                                        " repeater but with {len(inputs)} inputs"
            i1, i2 = inputs    # This is True because of is_gate_repeater
            i1.set_inverted(self.assignment == 1)
            i2.set_inverted(not i1.is_inverted())

            # Since DNFs are all identities, they have only one variable
            for oR, dnf in self.get_dnfs().items():
                variables = tuple(dnf.list_variables())
                assert len(variables) == 1, f"Anomalous number of variables in a DNF of a repeater: {len(variables)}"
                iR = variables[0]
                oR.set_inverted(iR.is_inverted())
        else:
            assert len(outputs) == 2, f"Weird gate {self.name}@{self.start_addr}" \
                                        " non-repeater but with {len(outputs)} outputs"
            o1, o2 = outputs
            o1.set_inverted(self.assignment == 1)
            o2.set_inverted(not o1.is_inverted())

    def get_register_location(self, expr):
        if expr in self.cache_register_location:
            return self.cache_register_location[expr]
        else:
            solver = claripy.Solver()
            for rl in self.register_locations:
                if solver.is_true(rl.expr == expr):
                    self.cache_register_location[expr] = rl
                    return rl
            return None

    def __compute_dnfs(self):
        # This step is performed in different substeps:
        # 1. Track dependencies in the gate
        GST = self.__track_behavior()
        dep_forest = GST.get_raw_forest()
        dep_forest.collapse(GST.memreads.keys())

        # After collapsing, only instructions that access memory (i.e., that
        # reads or sets weird registers) 

        # 2. Build the DNFs
        # The roots are the instructions that set weird registers
        solver = claripy.Solver()
        self.register_locations = []

        def get_instruction_read_memory_addresses(addr: int):
            read_addresses = GST.get_memaddresses(addr)
            assert len(read_addresses) == 1, f"An instruction can read from more than one address?"
            expr = read_addresses[0]
            return expr

        for oR in dep_forest.roots():
            expr = get_instruction_read_memory_addresses(oR)
            if not any(solver.is_true(expr == x.expr) for x in self.register_locations if x.is_output()):
                self.register_locations.append(wr.OutputRegisterLocation(expr))
            for iR in dep_forest.forest[oR]:
                expr = get_instruction_read_memory_addresses(iR)
                if not any(solver.is_true(expr == x.expr) for x in self.register_locations if x.is_input()):
                    self.register_locations.append(wr.InputRegisterLocation(expr))

        # Build DNFs: we append to each list the minterm given by a tree in the forest
        # By assigning different trees to the same OutputRegisterLocation we
        # get the list of minterms to be ORed together to get the DNF which is
        # implemented in a RegisterLocation
        dnfs_dict = defaultdict(list)
        for r in dep_forest.roots():
            expr = get_instruction_read_memory_addresses(r)
            oR = self.get_register_location(expr)
            iRs = [self.get_register_location(get_instruction_read_memory_addresses(x)) for x in dep_forest.forest[r]]
            dnfs_dict[oR].append(iRs)
        
        # In the end, we build a DNF with the lists we created before
        dnfs = {k: DNF(v) for k, v in dnfs_dict.items()}
        
        return dnfs

    def __reverse(self):
        assert not hasattr(self, "dnfs")
        self.dnfs = self.__compute_dnfs()

    def get_dnfs(self):
        assert hasattr(self, "dnfs")
        return self.dnfs

class WeirdGatesCollection:
    def __init__(self):
        self.wg = {}
    
    # start_addr: Address of the transient part of the gate
    def add(self, parser, start_addr, delta):
        if not start_addr in self.wg:
            self.wg[start_addr] = WeirdGate(parser, start_addr, delta)
        else:
            assert self.wg[start_addr].delta == delta, f"There are two different weird gates at address {start_addr}"
        return self.wg[start_addr]

    def find(self, address):
        return self.wg[address] if address in self.wg else None

class WiredWeirdGate:
    def __init__(self, wg: WeirdGate, call_addr: int, state: angr.SimState, wrs):
        self.wg = wg
        self.call_addr = call_addr
        
        # Assign values to weird registers that this gate uses
        outputs = self.wg.get_output_locations()
        output_wrs = {}
        for k, o in enumerate(outputs):
            wrl = o.eval(state, self.wg.symbolic_registers)
            wr = wrs.find(wrl)
            value = values.GateOutput(self, o.is_inverted(), k)
            wr.set_value(value)
            output_wrs[o] = wr

        if not self.wg.is_gate_repeater():
            t = tuple(output_wrs.values())
            wr1, wr2 = t[0], t[1]
            wr1.set_dual(wr2)
            wr2.set_dual(wr1)
        
        inputs = self.wg.get_input_locations()
        input_wrs = {}
        for i in inputs:
            wrl = i.eval(state, self.wg.symbolic_registers)
            wri = wrs.find(wrl)
            input_wrs[i] = wri
            assert wri.get_value() is not None
            if wri.get_dual() is None:
                # Look in the inputs for a possible dual
                for i2 in inputs:
                    wrl2 = i2.eval(state, self.wg.symbolic_registers)
                    wrj = wrs.find(wrl2)
                    if wrj.get_value().complementary(wri.get_value()):
                        wrj.set_dual(wri)
                        wri.set_dual(wrj)
                        break
                else:
                    raise Exception("Duals not found for two input weird register in gate {self}")
        
        self.outputs = output_wrs
        self.inputs = input_wrs

    def get_outputs(self, inverted):
        return [o for o in self.outputs.values() if o.get_value().is_inverted() == inverted]

    def get_inputs(self, inverted):
        return [o for o in self.inputs.values() if o.get_value().is_inverted() == inverted]

    def __str__(self):
        return f"{self.wwg.wg.start_addr}@{self.wwg.call_addr}"

    def __eq__(self, other):
        if not isinstance(other, WiredWeirdGate): return False
        return self.call_addr == other.call_addr and \
                self.wg.start_addr == other.wg.start_addr

    def str_call_addr(self):
        return '.'.join([str(x) for x in self.call_addr])

    def get_all_truth_tables(self):
        if not hasattr(self, "tt"):
            gate_dnfs = self.wg.get_dnfs()
            self.tt = {self.outputs[k]: TruthTable(d, self.inputs) for k, d in gate_dnfs.items()}
        return self.tt

    def get_truth_tables(self, inverted):
        return {k: v for k, v in self.get_all_truth_tables().items() if k.get_value().is_inverted() == inverted}

class WiredWeirdGatesCollection:
    def __init__(self):
        self.wwg = {}
    
    def add(self, wg: WeirdGate, call_addr: int, state: angr.SimState, wrs):
        if call_addr not in self.wwg:
            w = WiredWeirdGate(wg, call_addr, state, wrs)
            self.wwg[call_addr] = w
        else:
            w = self.wwg[call_addr]
        return w

    def iterator(self):
        return self.wwg.values()

    def fix_duals(self):
        for a, wwg in self.wwg.items():
            if wwg.wg.is_gate_repeater():
                noninv_outputs = wwg.get_outputs(False)
                inv_outputs = wwg.get_outputs(True)

                for oR in noninv_outputs:
                    if oR.get_dual() is None:
                        for ioR in inv_outputs:
                            if ioR.get_value().complementary(oR.get_value()):
                                ioR.set_dual(oR)
                                oR.set_dual(ioR)
                                break
                        else:
                            raise Exception("Unable to find duals for output weird registers of {wwg.call_addr}")
