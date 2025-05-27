from machine import Timer
from dht_temp_hum import DHTSensor
from i2cslave import I2CSlave
from dimmer import Dimmer
import ustruct
import time
from slave_controller import Slave


class I2CDeviceController:
    def __init__(self):
        # Dispositivos
        self.i2c = I2CSlave(address=0x0A, sda=14, scl=15)
        self.sensor = DHTSensor(pin=16, name="Interior", num_readings=5)
        self.dimmer = Dimmer(zx_pin_num=2, triac_pin_num=3)
        self.timer = Timer()
        
        # Estado del dispositivo
        self.temperature = 0.0
        self.humidity = 0.0
        self.power = 0.0
        self.running = True

    def start(self):
        #nicia todas las operaciones
        # Configurar timer para lecturas del sensor
        self.timer.init(mode=Timer.PERIODIC, period=2000, callback=self._update_sensor)
        print("Dispositivo esclavo iniciado")

    def stop(self):
        #Limpia recursos al terminar
        self.running = False
        self.timer.deinit()
        self.dimmer.set_power(0)  # Apagar al salir
        self.i2c.deInit()
        print("Dispositivo detenido")

    def _update_sensor(self, timer):
        #Actualiza las lecturas del sensor
        if self.sensor.measure():
            self.temperature, self.humidity = self.sensor.get_values()
            print(f"Medición: {self.temperature}°C, {self.humidity}%")

    def _handle_i2c_communication(self):
        # 1. Manejar lectura de potencia
        if self.i2c.waitForData(timeout=0):
            try:
                data = self.i2c.read()
                if len(data) == 4:
                    self.power = ustruct.unpack('<f', data)[0]  # Extraer el float de la tupla
                    self.dimmer.set_power(self.power)
                    print(f"Potencia actualizada: {self.power}%")
            except Exception as e:
                print(f"Error al procesar potencia: {e}")

        # 2. Manejar solicitudes de temperatura
        if self.i2c.waitForRdReq(timeout=0):
            self.i2c.write(ustruct.pack('<ff', self.temperature, self.humidity))

    def run(self):
        try:
            while self.running:
                self._handle_i2c_communication()
                #time.sleep_ms(100)
        except KeyboardInterrupt:
            self.stop()

def main():
    rp2040 = Slave()
    rp2040.start()
    rp2040.run()

if __name__ == '__main__':
    main()
