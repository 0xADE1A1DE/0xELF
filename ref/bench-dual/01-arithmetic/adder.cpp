#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_adder(
    byte* a, byte* b, byte* f, byte* cOut
) {}

int main(int argc, char* argv[]) {
	byte a[16], b[16], f[16], cOut[16];

	__weird__bench_adder(a, b, f, cOut);

	return 0;
}
