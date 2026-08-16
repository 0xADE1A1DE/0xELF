#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_router(
    byte* dest_x, byte* dest_y, byte* outport
) {}

int main(int argc, char* argv[]) {
	byte dest_x[4], dest_y[4], outport[4];

 	__weird__bench_router(dest_x, dest_y, outport);
	return 0;
}
