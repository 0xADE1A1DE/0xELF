#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_bar(
    byte* a, byte* shift, byte* result
) {}

int main(int argc, char* argv[]) {
	byte a[16], shift[1], result[16];

	__weird__bench_bar(a, shift, result);

	return 0;
}
