#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_cavlc(
    byte* totalcoeffs, byte* ctable, byte* trailingones, byte* coeff_token, byte* ctoken_len
) {}

int main(int argc, char* argv[]) {
	byte totalcoeffs[1], ctable[1], trailingones[1], coeff_token[1], ctoken_len[1];
	__weird__bench_cavlc(totalcoeffs, ctable, trailingones, coeff_token, ctoken_len);
	return 0;
}
