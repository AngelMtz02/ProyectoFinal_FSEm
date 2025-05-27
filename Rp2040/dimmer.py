from machine import Pin
from utime import sleep_ms
import rp2

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def dimmer():
    set(pin, 0)
    pull()
    mov(x, osr)

    label('waitzx')
    wrap_target()
    wait(0, pin, 0)

    pull(noblock)
    mov(x, osr)
    mov(y, x)

    wait(1, pin, 0)
    nop() [4]

    label('delay')
    jmp(y_dec, 'delay')

    set(pins, 1)
    set(pins, 0)

    jmp('waitzx')
    wrap()

class Dimmer:
    def __init__(self, zx_pin_num=2, triac_pin_num=3, freq=5000, sm_id=0):
        self.zxpin = Pin(zx_pin_num, Pin.IN)
        self.trpin = Pin(triac_pin_num, Pin.OUT)
        self.sm = rp2.StateMachine(sm_id, dimmer, freq=freq, in_base=self.zxpin, set_base=self.trpin)
        self.sm.active(1)

    def set_power(self, power_percent):
        """Establece la potencia del foco (0 a 100%) con apagado completo garantizado"""
        if not (0 <= power_percent <= 100):
            raise ValueError("El porcentaje debe estar entre 0 y 100.")
        
        # Manejo especial para apagado completo
        if power_percent <= 0.1:  # Considera valores mínimos como apagado
            delay = 31  # Valor mayor que el máximo normal para forzar apagado
        else:
            delay = 21 - int(21 * power_percent / 100)
        
        self.sm.put(delay)
        return True

    def loop_demo(self):
        """Modo de prueba: sube y baja la potencia del foco automáticamente."""
        while True:
            for power in range(0, 101):
                self.set_power(power)
                print(f'Subiendo: {power}%')
                sleep_ms(250)
            for power in range(100, -1, -1):
                self.set_power(power)
                print(f'Bajando: {power}%')
                sleep_ms(250)
