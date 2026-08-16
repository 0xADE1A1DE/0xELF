module _Z14__weird__mul16PhS_S_S_(
  input [15:0] _in1,
  input [15:0] _in2,
  output [31:0] _out
);
  wire [7:0] __94085128662352;
  wire [63:0] _conv;
  wire [7:0] __94085128666672;
  wire [63:0] _conv2;
  wire [63:0] __94085128668528;
  wire [63:0] _shl27;
  wire [7:0] __94085128668832;
  wire [63:0] _conv29;
  wire [7:0] __94085128669296;
  wire [63:0] _conv31;
  wire [63:0] __94085128669664;
  wire [63:0] _shl58;
  wire [63:0] _mul;
  wire [7:0] _conv62;
  wire [63:0] _shr64;
  wire [7:0] _conv66;
  wire [63:0] _shr68;
  wire [7:0] _conv70;
  wire [63:0] _shr72;
  wire [7:0] _conv74;

  assign __94085128662352 = _in1[7:0];
  assign _conv[7:0] = __94085128662352;
  assign _conv[63:8] = 0;
  assign __94085128666672 = _in1[15:8];
  assign _conv2[7:0] = __94085128666672;
  assign _conv2[63:8] = 0;
  assign __94085128668528 = _conv2 << 8;
  assign _shl27 = __94085128668528 | _conv;
  assign __94085128668832 = _in2[7:0];
  assign _conv29[7:0] = __94085128668832;
  assign _conv29[63:8] = 0;
  assign __94085128669296 = _in2[15:8];
  assign _conv31[7:0] = __94085128669296;
  assign _conv31[63:8] = 0;
  assign __94085128669664 = _conv31 << 8;
  assign _shl58 = __94085128669664 | _conv29;
  assign _mul = _shl58 * _shl27;
  assign _conv62 = _mul[7:0];
  assign _out[7:0] = _conv62;
  assign _shr64 = _mul >> 8;
  assign _conv66 = _shr64[7:0];
  assign _out[15:8] = _conv66;
  assign _shr68 = _mul >> 16;
  assign _conv70 = _shr68[7:0];
  assign _out[23:16] = _conv70;
  assign _shr72 = _mul >> 24;
  assign _conv74 = _shr72[7:0];
  assign _out[31:24] = _conv74;
endmodule
