import dht
from machine import Pin
from time import sleep

class DHTSensor:
    def __init__(self, pin, name, num_readings=3):
        self.sensor = dht.DHT11(Pin(pin))
        self.name = name
        self.num_readings = num_readings
        self.temp_readings = []
        self.hum_readings = []

    def measure(self):
        """Toma una nueva medición y actualiza los promedios."""
        try:
            self.sensor.measure()
            temp = self.sensor.temperature()
            hum = self.sensor.humidity()

            self.temp_readings.append(temp)
            self.hum_readings.append(hum)

            if len(self.temp_readings) > self.num_readings:
                self.temp_readings.pop(0)
                self.hum_readings.pop(0)

            return True
        except Exception as e:
            print(f"[ERROR] {self.name}: {str(e)}")
            return False

    def get_values(self):
        if len(self.temp_readings) < 1:
            return None, None
        avg_temp = sum(self.temp_readings) / len(self.temp_readings)
        avg_hum = sum(self.hum_readings) / len(self.hum_readings)
        return round(avg_temp, 1), round(avg_hum, 1)

def main():
    # Configuración del sensor (ajusta el pin según tu conexión)
    sensor = DHTSensor(pin=16, name="Interior", num_readings=5)
    
    print(f"Iniciando monitorización con {sensor.name}")
    print("Presiona Ctrl+C para detener")
    print("----------------------------------")
    
    try:
        while True:
            if sensor.measure():
                temp, hum = sensor.get_values()
                if temp is not None and hum is not None:
                    print(f"{sensor.name}: {temp}°C, {hum}% humedad")
                else:
                    print("Esperando datos válidos...")
            
            # Intervalo entre lecturas (DHT11 necesita al menos 1 segundo)
            sleep(2)
            
    except KeyboardInterrupt:
        print("\nMonitorización detenida")
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")

#if __name__ == "__main__":
 #   main()