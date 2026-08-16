module __weird__sha1_round2(
  input [159:0] _input,
  input [31:0] _w,
  output [159:0] _output
);
  wire [31:0] __94818028348528;
  wire [31:0] __94818028348832;
  wire [31:0] __94818028349136;
  wire [31:0] __94818028349504;
  wire [31:0] __94818028349824;
  wire [31:0] _xor;
  wire [31:0] _xor5;
  wire [31:0] _or;
  wire [31:0] _add;
  wire [31:0] _add6;
  wire [31:0] _add7;
  wire [31:0] _add8;
  wire [31:0] _or13;
  wire [31:0] _error_output;
  wire [31:0] _and;
  wire _tobool;

  assign __94818028348528 = _input[31:0];
  assign __94818028348832 = _input[63:32];
  assign __94818028349136 = _input[95:64];
  assign __94818028349504 = _input[127:96];
  assign __94818028349824 = _input[159:128];
  assign _xor = __94818028349136 ^ __94818028348832;
  assign _xor5 = _xor ^ __94818028349504;
  assign _or = ({ __94818028348528, __94818028348528 } << (5 % 32)) >> 32;
  assign _add = _w + 1859775393;
  assign _add6 = _add + _or;
  assign _add7 = _add6 + _xor5;
  assign _add8 = _add7 + __94818028349824;
  assign _output[31:0] = _add8;
  assign _output[63:32] = __94818028348528;
  assign _or13 = ({ __94818028348832, __94818028348832 } << (30 % 32)) >> 32;
  assign _output[95:64] = _or13;
  assign _output[127:96] = __94818028349136;
  assign _output[159:128] = __94818028349504;
  assign _error_output[31:0] = _xor5;
  assign _and = _xor5 & 1;
  assign _tobool = _and != 0;
endmodule
