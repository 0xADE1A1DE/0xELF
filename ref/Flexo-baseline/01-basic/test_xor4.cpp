bool __weird__xor4(bool in1, bool in2, bool in3, bool in4, bool& out) {
    out = in1 ^ in2 ^ in3 ^ in4;
    return out;
}

int main(void) {
	bool b1 = true, b2 = false, b3 = true, b4=false;
	bool out;
	bool ec;

	ec = __weird__xor4(b1, b2, b3, b4, out);
	return ec;
}
