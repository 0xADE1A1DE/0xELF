module __weird__sha1_round(
  input [159:0] _input,
  input [31:0] _w,
  output [159:0] _output
);
  wire [31:0] __94324467979776;
  wire [31:0] __94324467980080;
  wire [31:0] __94324467980384;
  wire [31:0] __94324467980752;
  wire [31:0] __94324467981072;
  wire [31:0] _and;
  wire [31:0] _not;
  wire [31:0] _and5;
  wire [31:0] _or;
  wire [31:0] _or6;
  wire [31:0] _add;
  wire [31:0] _add7;
  wire [31:0] _add8;
  wire [31:0] _add9;
  wire [31:0] _or14;
  wire [31:0] _error_output;
  wire [31:0] _and19;
  wire _tobool;

  assign __94324467979776 = _input[31:0];
  assign __94324467980080 = _input[63:32];
  assign __94324467980384 = _input[95:64];
  assign __94324467980752 = _input[127:96];
  assign __94324467981072 = _input[159:128];
  assign _and = __94324467980384 & __94324467980080;
  assign _not = __94324467980080 ^ 4294967295;
  assign _and5 = __94324467980752 & _not;
  assign _or = _and5 | _and;
  assign _or6 = ({ __94324467979776, __94324467979776 } << (5 % 32)) >> 32;
  assign _add = _w + 1518500249;
  assign _add7 = _add + _or6;
  assign _add8 = _add7 + __94324467981072;
  assign _add9 = _add8 + _or;
  assign _output[31:0] = _add9;
  assign _output[63:32] = __94324467979776;
  assign _or14 = ({ __94324467980080, __94324467980080 } << (30 % 32)) >> 32;
  assign _output[95:64] = _or14;
  assign _output[127:96] = __94324467980384;
  assign _output[159:128] = __94324467980752;
  assign _error_output[31:0] = _or;
  assign _and19 = _or & 1;
  assign _tobool = _and19 != 0;
endmodule
