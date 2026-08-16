bool __weird__xor(bool in1, bool in2, bool& out) {
    out = in1 ^ in2;
    return out;
}

int main(void) {
	bool b1 = true, b2 = false;
	bool out;
	bool ec;

	ec = __weird__xor(b1, b2, out);
	return ec;
}
