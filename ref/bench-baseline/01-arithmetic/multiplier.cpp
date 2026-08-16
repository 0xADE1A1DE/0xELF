#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_multiplier(
    byte* a, byte* b, byte* f
) {}

int main(int argc, char* argv[]) {
	byte a[8], b[8], f[16];

	__weird__bench_multiplier(a, b, f);

	return 0;
}
