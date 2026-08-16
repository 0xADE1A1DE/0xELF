module _Z13__weird__mul8PhS_S_S_(
  input [7:0] _in1,
  input [7:0] _in2,
  output [15:0] _out
);
  wire [7:0] __94312226168144;
  wire [63:0] _conv;
  wire [7:0] __94312226171264;
  wire [63:0] _conv29;
  wire [63:0] _mul;
  wire [7:0] _conv62;
  wire [63:0] _shr64;
  wire [7:0] _conv66;

  assign __94312226168144 = _in1[7:0];
  assign _conv[7:0] = __94312226168144;
  assign _conv[63:8] = 0;
  assign __94312226171264 = _in2[7:0];
  assign _conv29[7:0] = __94312226171264;
  assign _conv29[63:8] = 0;
  assign _mul = _conv29 * _conv;
  assign _conv62 = _mul[7:0];
  assign _out[7:0] = _conv62;
  assign _shr64 = _mul >> 8;
  assign _conv66 = _shr64[7:0];
  assign _out[15:8] = _conv66;
endmodule
