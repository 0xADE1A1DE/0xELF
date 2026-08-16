module _Z16__weird__adder24PhS_S_S_(
  input [23:0] _in1,
  input [23:0] _in2,
  output [23:0] _out
);
  wire [7:0] __94505420631408;
  wire [63:0] _conv;
  wire [7:0] __94505420635728;
  wire [63:0] _conv2;
  wire [7:0] __94505420637760;
  wire [63:0] _conv4;
  wire [63:0] __94505420638112;
  wire [63:0] __94505420638304;
  wire [63:0] __94505420638528;
  wire [63:0] _shl27;
  wire [7:0] __94505420638816;
  wire [63:0] _conv29;
  wire [7:0] __94505420639648;
  wire [63:0] _conv31;
  wire [7:0] __94505420640112;
  wire [63:0] _conv35;
  wire [63:0] __94505420640544;
  wire [63:0] __94505420640688;
  wire [63:0] __94505420640832;
  wire [63:0] _shl58;
  wire [63:0] _add60;
  wire [7:0] _conv63;
  wire [63:0] _shr65;
  wire [7:0] _conv67;
  wire [63:0] _shl61;
  wire [7:0] _conv71;

  assign __94505420631408 = _in1[7:0];
  assign _conv[7:0] = __94505420631408;
  assign _conv[63:8] = 0;
  assign __94505420635728 = _in1[15:8];
  assign _conv2[7:0] = __94505420635728;
  assign _conv2[63:8] = 0;
  assign __94505420637760 = _in1[23:16];
  assign _conv4[7:0] = __94505420637760;
  assign _conv4[63:8] = 0;
  assign __94505420638112 = _conv4 << 16;
  assign __94505420638304 = _conv2 << 8;
  assign __94505420638528 = __94505420638304 | _conv;
  assign _shl27 = __94505420638528 | __94505420638112;
  assign __94505420638816 = _in2[7:0];
  assign _conv29[7:0] = __94505420638816;
  assign _conv29[63:8] = 0;
  assign __94505420639648 = _in2[15:8];
  assign _conv31[7:0] = __94505420639648;
  assign _conv31[63:8] = 0;
  assign __94505420640112 = _in2[23:16];
  assign _conv35[7:0] = __94505420640112;
  assign _conv35[63:8] = 0;
  assign __94505420640544 = _conv35 << 16;
  assign __94505420640688 = _conv31 << 8;
  assign __94505420640832 = __94505420640688 | _conv29;
  assign _shl58 = __94505420640832 | __94505420640544;
  assign _add60 = _shl58 + _shl27;
  assign _conv63 = _add60[7:0];
  assign _out[7:0] = _conv63;
  assign _shr65 = _add60 >> 8;
  assign _conv67 = _shr65[7:0];
  assign _out[15:8] = _conv67;
  assign _shl61 = _add60 >> 16;
  assign _conv71 = _shl61[7:0];
  assign _out[23:16] = _conv71;
endmodule
