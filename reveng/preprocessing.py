#!/usr/bin/env python3

import json
from collections import deque, defaultdict

import angr

class ELF_Preprocessor:
    def __init__(self, elf_filename):
        self.elf_filename = elf_filename
        self.angr_proj = angr.Project(elf_filename, auto_load_libs=False)
        self.cfg = self.angr_proj.analyses.CFGFast(
            normalize=True,
            data_references=True,
            cross_references=False,
        )

    def __list_functions_reachable_from(self, kb, start_func):
        callgraph = kb.functions.callgraph
        seen = set()
        q = deque([start_func.addr])
        out = {}

        while q:
            faddr = q.popleft()
            if faddr in seen:
                continue
            seen.add(faddr)

            func = kb.functions.get(faddr, None)
            if func is None:
                continue

            out[faddr] = func

            if faddr not in callgraph:
                continue

            for callee_addr in callgraph.successors(faddr):
                if callee_addr not in seen:
                    q.append(callee_addr)

        return out

    def __address_to_function(self, address):
        func = self.angr_proj.kb.functions.get(address, None)
        if func is None:
            raise ValueError(f"No function found at address {hex(func_spec)}")
        return func

    def find_timestamps(self, start_address):
        if not hasattr(self, "timestamps"):
            timestamps = defaultdict(list)
            start = self.__address_to_function(start_address)
            reachable = self.__list_functions_reachable_from(self.angr_proj.kb, start)
            for faddr in reachable:
                func = reachable[faddr]
                for block in func.blocks:
                    for insn in block.capstone.insns:
                        if insn.mnemonic == "rdtscp" or insn.mnemonic == "rdtsc":
                            timestamps[insn.mnemonic].append(insn.address)
            self.timestamps = timestamps
        return self.timestamps
