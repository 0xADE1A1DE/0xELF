#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_int2float(
    byte* B, byte* M, byte* E
) {}

int main(int argc, char* argv[]) {
	byte B[2], M[1], E[1];

 	__weird__bench_int2float(B, M, E);
	return 0;
}
