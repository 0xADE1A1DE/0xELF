#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_sqrt(
    byte* a, byte* asqrt
) {}

int main(int argc, char* argv[]) {
	byte a[16], asqrt[8];

	__weird__bench_sqrt(a, asqrt);

	return 0;
}
