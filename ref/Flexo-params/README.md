# Executables with different Flexo parameters

This directory contains different executables compiled with non-default Flexo parameters.

We consider the following parameters:

- `WM_DELAY`: The iterations of the delay loop between gate executions. Default to 256.
- `WM_USE_FENCE`: Use memory fences instead of using a delay loop. Default to true.
- `DUAL_WM_MAX_INPUT`: The maximum input size of a weird gate. Default to 4.
- `WM_MAX_FANOUT`: The max number of fan-outs of an assign gate. Default to 3.
- `WR_MAPPING`: The mapping type of weird registers, which can be Baseline or Shuffle (default).
- `WR_OFFSET`: The memory offset (in bytes) between each weird registers. Default to 960.
- `WR_FAKE_OFFSET`: The memory offset (in bytes) between a real weird register and its fake location. Default to 512.
- `WR_SYSCALL_RAND`: Use Linux syscall to generate random numbers instead of using standard library calls. Default to false
- `WR_USE_MMAP`: Call the mmap syscall to allocate memory for WR instead of using the stack memory. May be slower if enabled, but this supports circuits with more wires. Default to false.

Therefore, we use the following naming scheme for each file:

```
<name_as_in_Flexo>-<delay>-<use_fence>-<dual_wm_max_input>-<max_fanout>-<wr_mapping>-<wr_offset>-<wr_fake_offset>-<wr_hit_threshold>-<wr_syscall_rand>-<wr_use_mmap>.elf
```

An empty value means that the value is not specified.

In particular, we consider these new values for the parameters

1. `WM_USE_FENCE = False`
2. `WM_USE_FENCE = False` and `WM_DELAY = 1024`
3. `WR_OFFSET = 4160`
4. `WR_FAKE_OFFSET = 720`
5. `WR_OFFSET = 960` and `WR_FAKE_OFFSET = 960`
6. `WR_SYSCALL_RAND = True`
7. `WR_USE_MMAP = True`
