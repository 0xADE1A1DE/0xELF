bool __weird__and(bool in1, bool in2, bool& out) {
    out = in1 & in2;
    return out;
}

int main(void) {
	bool b1 = true, b2 = false;
	bool out;
	bool ec;

	ec = __weird__and(b1, b2, out);
	return ec;
}
