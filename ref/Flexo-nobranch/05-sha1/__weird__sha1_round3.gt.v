module __weird__sha1_round3(
  input [159:0] _input,
  input [31:0] _w,
  output [159:0] _output
);
  wire [31:0] __94818028291552;
  wire [31:0] __94818028291856;
  wire [31:0] __94818028292160;
  wire [31:0] __94818028292528;
  wire [31:0] __94818028292848;
  wire [31:0] _and541;
  wire [31:0] _or;
  wire [31:0] _and6;
  wire [31:0] _or7;
  wire [31:0] _or8;
  wire [31:0] _add;
  wire [31:0] _add9;
  wire [31:0] _add10;
  wire [31:0] _add11;
  wire [31:0] _or16;
  wire [31:0] _error_output;
  wire [31:0] _and21;
  wire _tobool;

  assign __94818028291552 = _input[31:0];
  assign __94818028291856 = _input[63:32];
  assign __94818028292160 = _input[95:64];
  assign __94818028292528 = _input[127:96];
  assign __94818028292848 = _input[159:128];
  assign _and541 = __94818028292528 | __94818028292160;
  assign _or = _and541 & __94818028291856;
  assign _and6 = __94818028292528 & __94818028292160;
  assign _or7 = _or | _and6;
  assign _or8 = ({ __94818028291552, __94818028291552 } << (5 % 32)) >> 32;
  assign _add = _w + 2400959708;
  assign _add9 = _add + _or8;
  assign _add10 = _add9 + __94818028292848;
  assign _add11 = _add10 + _or7;
  assign _output[31:0] = _add11;
  assign _output[63:32] = __94818028291552;
  assign _or16 = ({ __94818028291856, __94818028291856 } << (30 % 32)) >> 32;
  assign _output[95:64] = _or16;
  assign _output[127:96] = __94818028292160;
  assign _output[159:128] = __94818028292528;
  assign _error_output[31:0] = _or7;
  assign _and21 = _or7 & 1;
  assign _tobool = _and21 != 0;
endmodule
