class Valve:
    def __init__(self, pin):
        self.pin = pin
        self.close()  # Al crear la válvula, aseguramos que esté cerrada

    def open(self):
        self.pin.value(1)

    def close(self):
        self.pin.value(0)

    def is_open(self):
        return self.pin.value() == 1
