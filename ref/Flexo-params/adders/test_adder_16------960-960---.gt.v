module _Z16__weird__adder16PhS_S_S_(
  input [15:0] _in1,
  input [15:0] _in2,
  output [15:0] _out
);
  wire [7:0] __94299615911280;
  wire [63:0] _conv;
  wire [7:0] __94299615915600;
  wire [63:0] _conv2;
  wire [63:0] __94299615917456;
  wire [63:0] _shl27;
  wire [7:0] __94299615917760;
  wire [63:0] _conv29;
  wire [7:0] __94299615918224;
  wire [63:0] _conv31;
  wire [63:0] __94299615918592;
  wire [63:0] _shl58;
  wire [63:0] _add60;
  wire [7:0] _conv63;
  wire [63:0] _shl61;
  wire [7:0] _conv67;

  assign __94299615911280 = _in1[7:0];
  assign _conv[7:0] = __94299615911280;
  assign _conv[63:8] = 0;
  assign __94299615915600 = _in1[15:8];
  assign _conv2[7:0] = __94299615915600;
  assign _conv2[63:8] = 0;
  assign __94299615917456 = _conv2 << 8;
  assign _shl27 = __94299615917456 | _conv;
  assign __94299615917760 = _in2[7:0];
  assign _conv29[7:0] = __94299615917760;
  assign _conv29[63:8] = 0;
  assign __94299615918224 = _in2[15:8];
  assign _conv31[7:0] = __94299615918224;
  assign _conv31[63:8] = 0;
  assign __94299615918592 = _conv31 << 8;
  assign _shl58 = __94299615918592 | _conv29;
  assign _add60 = _shl58 + _shl27;
  assign _conv63 = _add60[7:0];
  assign _out[7:0] = _conv63;
  assign _shl61 = _add60 >> 8;
  assign _conv67 = _shl61[7:0];
  assign _out[15:8] = _conv67;
endmodule
