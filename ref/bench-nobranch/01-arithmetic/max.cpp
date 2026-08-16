#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_max(
    byte* in0, byte* in1,byte* in2,byte* in3, byte* result
) {}

int main(int argc, char* argv[]) {
	byte in0[16], in1[16], in2[16], in3[16], result[16];

	__weird__bench_max(in0, in1, in2, in3, result);

	return 0;
}
