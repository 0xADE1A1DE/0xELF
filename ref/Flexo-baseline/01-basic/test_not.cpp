bool __weird__not(bool in1, bool& out) {
    out = !in1;
    return out;
}

int main(void) {
	bool b1 = true;
	bool out;
	bool ec;

	ec = __weird__not(b1, out);
	return ec;
}
