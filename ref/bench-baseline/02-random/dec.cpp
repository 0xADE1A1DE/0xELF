#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_dec(
    byte count, byte *selectp1, byte *selectp2
) {}

int main(int argc, char* argv[]) {
	byte count, selectp1[16], selectp2[16];

 	__weird__bench_dec(count, selectp1, selectp2);
	return 0;
}
