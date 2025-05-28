class DCFan:
    def __init__(self, pin1, pin2, enable_pin, min_duty=15000, max_duty=55535):
        self.pin1 = pin1
        self.pin2 = pin2
        self.enable_pin = enable_pin
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.speed = 0

    def on(self, speed):
        self.speed = speed
        duty = self.duty_cycle(self.speed)
        print(f'Set speed: {speed}%, Duty cycle enviado: {duty}/65535')
        self.enable_pin.duty_u16(duty)
        self.pin1.value(0)
        self.pin2.value(1)

    
    def backwards(self, speed_percent):
        self.speed = speed_percent
        duty = self.duty_cycle(self.speed)
        self.enable_pin.duty_u16(duty)
        self.pin1.value(1)
        self.pin2.value(0)   # Corrijo la dirección aquí para backwards

    def stop(self):
        self.enable_pin.duty_u16(0)
        self.pin1.value(0)
        self.pin2.value(0)

    def duty_cycle(self, speed_percent):
        if speed_percent <= 0:
            return 0
        elif speed_percent >= 100:
            return 65535
        else:
            return int(self.min_duty + (self.max_duty - self.min_duty) * (speed_percent / 100))
