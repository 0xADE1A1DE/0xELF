import random

class OxELFBehavior:
    def __init__(self):
        pass

    def get_assignment(self):
        raise NotImplemented()

class DeterministicOxELF(OxELFBehavior):
    def __init__(self, defaultassignment=0):
        self.default=defaultassignment
        pass

    def get_assignment(self):
        return self.default

class NonDeterministicOxELF(OxELFBehavior):
    def __init__(self, seed):
        self.seed = seed
        random.seed(seed)
        pass

    def get_assignment(self):
        return random.randint(0,1)

behavior: OxELFBehavior | None = None

def get_assignment():
    assert behavior is not None, f"OxELF behavior has not been initialized"
    return behavior.get_assignment()
