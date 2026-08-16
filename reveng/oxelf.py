#!/usr/bin/env python3
import sys
import random
import argparse

import rand

parser = argparse.ArgumentParser(
                    prog='OxELF',
                    description='Reverse Engineering Framework for Flexo-generated Weird Machines')

subparsers = parser.add_subparsers(dest="command", required=True)
parser.add_argument('ELF', default=None, type=str, help="Input ELF file")
parser.add_argument('--seed', type=int, help="Seed for random initialization", default=None)
parser.add_argument('--deterministic', action="store_true", help="Require OxELF to always output the same file")
analyze_parser = subparsers.add_parser("analyze", help="Reverse engineer a weird function located in an ELF file")
analyze_parser.add_argument('function', type=str, help="Name or address of the weird function to analyze")
analyze_parser.add_argument('--arguments', type=int, default=6, help="Number of arguments of the weird function (an overestimation works fine)")
analyze_parser.add_argument('--iz', action="store_true", help="Ignore leading zeros of all outputs of the circuit")
info_parser = subparsers.add_parser("info", help="Get information on the given binary")
info_parser.add_argument('--list-symbols', action="store_true", help="Get a list of all the symbols in the binary")
disass_parser = subparsers.add_parser("disass", help="Get disassembly of given binary")
disass_parser.add_argument('--decimal', action="store_true", help="Addresses are reported as decimal numbers")
args = parser.parse_args()

if args.seed is None:
    seed = random.randint(1, 2**64-1)
else:
    seed = args.seed

if args.deterministic:
    if seed == 0 or seed == 1:
        rand.behavior = rand.DeterministicOxELF(seed)
    else:
        sys.stderr.write("WARNING: seed is either not set or set to a value" \
        "different from 0 or 1.\nEven if OxELF is deterministic, it needs an" \
        "arbitrary way to handle the negated attribute.\nUsing 0 by default\n")
        rand.behavior = rand.DeterministicOxELF(0)
    sys.stderr.write(f"Using deterministic behavior with decision = {rand.behavior.default}\n")
else:
    rand.behavior = rand.NonDeterministicOxELF(seed)
    sys.stderr.write(f"Using nondeterministic behavior with seed = {rand.behavior.seed}\n")

import elf
import preprocessing

e = elf.ELF(args.ELF)
if args.command == "analyze":
    if args.function is not None:
        try:
            fa = int(args.function, base=0)
        except:
            # NOTE: 0xELF by default requires the starting address of a Flexo weird function
            #       this is just a helper for a user to select the proper function
            st = e.get_symbol_table()
            assert args.function in st, f"{args.function} not recognized as a function name or address"
            fa = st[args.function]
    wf = e.build_weird_function(fa, args.arguments)
    wf.parse()
    print(wf.blif(args.iz))
elif args.command == "info":
    if args.list_symbols:
        sys.stderr.write("----- BINARY SYMBOLS FOUND -----\n")
        for s, a in e.get_symbol_table().items():
            print(f"{s} @ 0x{a:x}")
elif args.command == "disass":
    d = e.disass_all()
    for i in d:
        a = f'0x{i.address:x}' if not args.decimal else '{i.addr}'
        print(f"{a}\t{i.mnemonic}\t{i.op_str}")
