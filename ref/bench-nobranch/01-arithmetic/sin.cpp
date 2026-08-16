#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_sin(
    byte* a, byte* sin
) {}

int main(int argc, char* argv[]) {
	byte a[3], sin[4];

	__weird__bench_sin(a, sin);

	return 0;
}
