#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_log2(
    byte* a, byte* result
) {}

int main(int argc, char* argv[]) {
	byte a[4], result[4];

	__weird__bench_log2(a, result);

	return 0;
}
