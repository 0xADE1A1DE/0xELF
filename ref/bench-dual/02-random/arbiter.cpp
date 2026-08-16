#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <argp.h>
#include <time.h>
#include <vector>

typedef unsigned char byte;

void __weird__bench_arbiter(
    byte* priority, byte* req, byte* grant, byte* anyGrant
) {}

int main(int argc, char* argv[]) {
	byte priority[16], req[16], grant[16], anyGrant[1];
	__weird__bench_arbiter(priority, req, grant, anyGrant);
	return 0;
}
