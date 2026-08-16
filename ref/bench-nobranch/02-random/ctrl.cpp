#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_ctrl(
    byte* opcode, byte* op_ext, byte* sel_reg_dst, byte* sel_alu_opB, byte* alu_op, byte* halt, byte* reg_write, byte* sel_pc_opA, byte* sel_pc_opB, byte* beqz, byte* bnez, byte* bgez, byte* bltz, byte* jump, byte* Cin, byte* invA, byte* invB, byte* sign, byte* mem_write, byte* sel_wb
) {}

int main(int argc, char* argv[]) {
	byte opcode[1], op_ext[1];
	/* In Flexo, all outputs must be passed by pointer (or reference in C++) */
	byte sel_reg_dst[1], sel_alu_opB[1], alu_op[1], alu_op_ext[1], halt[1], reg_write[1], sel_pc_opA[1], sel_pc_opB[1], beqz[1], bnez[1], bgez[1], bltz[1], jump[1], Cin[1], invA[1], invB[1], sign[1], mem_write[1], sel_wb[1];

 	__weird__bench_ctrl(opcode, op_ext, sel_reg_dst, sel_alu_opB, alu_op, halt, reg_write, sel_pc_opA, sel_pc_opB, beqz, bnez, bgez, bltz, jump, Cin, invA, invB, sign, mem_write, sel_wb);
	return 0;
}
