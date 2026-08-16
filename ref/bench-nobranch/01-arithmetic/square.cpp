#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_square(
    byte* a, byte* square
) {}

int main(int argc, char* argv[]) {
	byte a[8], square[16];

	__weird__bench_square(a, square);

	return 0;
}
