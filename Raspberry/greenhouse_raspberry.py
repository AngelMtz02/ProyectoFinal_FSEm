# master.py

import smbus2
import struct
import time
from datetime import datetime
from logger import DataLogger

# --- PID constants ---
MAX_POWER = 100.0
MIN_POWER = 0.0
KP = 8.0
KI = 0.15
KD = 4.0
INTEGRAL_LIMIT = 25.0

# --- I2C settings ---
I2C_BUS = 1
SLAVE_ADDR = 0x0A
READ_INTERVAL = 2.2  # para sincronizar con dht11

i2c = smbus2.SMBus(I2C_BUS)

class PIDController:
    def __init__(self):
        self.prev_error = 0.0
        self.prev_time = time.time()
        self.integral = 0.0

    def compute(self, current, target):
        error = target - current
        now = time.time()
        dt = now - self.prev_time
        self.prev_time = now

        P = KP * error
        self.integral += error * dt
        # Anti-windup
        self.integral = max(-INTEGRAL_LIMIT, min(INTEGRAL_LIMIT, self.integral))
        I = KI * self.integral

        D = 0.0
        if dt > 0:
            D = KD * ((error - self.prev_error) / dt)

        self.prev_error = error

        power = P + I + D
        return max(MIN_POWER, min(MAX_POWER, power))

def get_valid_temperature():
    while True:
        try:
            val = float(input("Ingrese la temperatura deseada (30-100°C): "))
            if 30 <= val <= 100:
                return val
            print("Debe estar entre 30 y 100")
        except ValueError:
            print("Número inválido")

def try_read_slave():
    """Devuelve tupla (temp,hum) o (None,None)."""
    try:
        msg = smbus2.i2c_msg.read(SLAVE_ADDR, 8)
        i2c.i2c_rdwr(msg)
        data = bytes(msg)
        if len(data) == 8:
            t, h = struct.unpack('<ff', data)
            if -40 <= t <= 85 and 0 <= h <= 100:
                return t, h
    except (OSError, smbus2.SMBusTimeoutError):
        pass
    return None, None

def try_write_slave(power):
    """Envía la potencia (float)."""
    try:
        p = max(MIN_POWER, min(MAX_POWER, power))
        data = struct.pack('<f', p)
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)
        time.sleep(0.01)            # ← deja respirar al esclavo
        return True
    except OSError:
        return False

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def main():
    print("Iniciando maestro PID")
    controller = PIDController()
    logger = DataLogger()
    logger.start_time = time.time()

    target_temp = get_valid_temperature()
    print(f"Temperatura objetivo: {target_temp:.1f}°C")
    print(f"KP={KP}, KI={KI}, KD={KD}\n")

    power_sum = 0.0
    readings = 0

    try:
        while True:
            # 1) Leer primero temperatura/humedad
            temp, hum = try_read_slave()
            if temp is None:
                # no data => ciclo rápido de polling
                time.sleep(READ_INTERVAL)
                continue

            # 2) Calcular potencia con el dato recién leído
            power = controller.compute(temp, target_temp)

            # 3) Enviar potencia al esclavo
            if not try_write_slave(power):
                print("Error escritura I2C")

            # 4) Log y reporte
            logger.log_data(temp, hum, power, target_temp)
            print(f"[{get_current_time()}] Temp: {temp:.1f}°C | Hum: {hum:.1f}% | Power: {power:.1f}%")

            power_sum += power
            readings += 1

            # Pause ligera antes del siguiente polling
            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        pass
    finally:
        avg = (power_sum / readings) if readings else 0.0
        print(f"\nPotencia promedio: {avg:.2f}%")
        print(f"Constantes finales: KP={KP}, KI={KI}, KD={KD}")
        # Apagar esclavo y cerrar bus
        try_write_slave(0.0)
        i2c.close()
        print("Maestro detenido")

if __name__ == '__main__':
    main()
