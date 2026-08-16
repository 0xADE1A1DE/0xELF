#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_voter(
    byte* A, byte* maj
) {}

int main(int argc, char* argv[]) {
	byte A[128], maj[1];

 	__weird__bench_voter(A, maj);
	return 0;
}
