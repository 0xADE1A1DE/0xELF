`bench-*` directories contain the tests compiled from the EPFL benchmarking circuits
`Flexo-*` directories contain the default tests provided with the Flexo compiler

For each test we provide:
- The C++ source (filename ending with .cpp)
- The compiled binary with Flexo (filename ending with .elf)
- The weird function translated by Flexo to a combinational circuit in both Verilog (filename ending with .gt.v) and blif (filename ending with .gt.blif) formats
- The stripped version of the binary (filename ending with -s.elf)

The suffix of the directory indicates the value of `WR_TYPE` used for compiling (except for `Flexo-params`, which contains tests where we use other non-default parameters to test 0xELF).

# Licensing information

Source files (`*.cpp`) in `Flexo-*` directories come, or are adapted, from `https://github.com/joeywang4/Flexo` (see `LICENSE_Flexo`), while Verilog files (`*.v`) in `bench-*` directories come from `https://github.com/lsils/benchmarks` (see `LICENSE_benchmarking`).

All other files in this directory, including this README, are released under the terms of the Apache License version 2.0.
