from collections import namedtuple
# This class emulates the behavior of an RSB
# We assume the existence of an infinite RSB, which is enough for our purposes
class RSB_entry(namedtuple('RSB_entry', ['at_addr', 'to_addr', 'ret_addr', 'state'])):
    __slots__ = ()
    def __str__(self):
        return hex(self.at_addr)

class RSB:
    def __init__(self, include_dummy_parent_function=True):
        self.rsb = []

    def peek(self):
        return self.rsb[-1]

    # Record a call performed at at_address, which goes to to_address and
    # should return at ret_address
    def call(self, at_addr, to_addr, ret_addr, state):
        self.rsb.append(RSB_entry(at_addr, to_addr, ret_addr, state))

    # Pops an entry from the RSB.
    # This should be called when a ret instructions makes the execution return
    # at ret_addr
    # Returns True if the RSB correctly predicts the return address, False instead
    def ret(self):
        return self.rsb.pop()

    def is_empty(self):
        return len(self.rsb) == 0
