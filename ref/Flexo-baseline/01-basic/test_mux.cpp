bool __weird__mux(bool in1, bool in2, bool in3, bool& out) {
    out = ((in1 & !(in3)) | (in2 & in3));
    return out;
}

int main(void) {
	bool b1 = true, b2 = false, b3 = true;
	bool out;
	bool ec;

	ec = __weird__mux(b1, b2, b3, out);
	return ec;
}
