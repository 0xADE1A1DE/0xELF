#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_priority(
    byte* A, byte* P, byte* F
) {}

int main(int argc, char* argv[]) {
	byte A[2], P[1], F[1];

 	__weird__bench_priority(A, P, F);
	return 0;
}
