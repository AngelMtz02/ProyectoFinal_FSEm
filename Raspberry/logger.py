import csv
from datetime import datetime
import time
# Añade al inicio del código
LOG_FILE = "temp_control_log.csv"
LOG_INTERVAL = 5  # Segundos entre registros (para no saturar memoria)

class DataLogger:
    def __init__(self):
        self.last_log_time = time.time()
        self.file = open(LOG_FILE, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(["Timestamp", "Time (s)", "Temperature (°C)", "Humidity (%)", "Power (%)", "Desired Temperature"])

    def log_data(self, temp, hum,  power, DESIRED_TEMPERATURE):
        current_time = time.time()
        if current_time - self.last_log_time >= LOG_INTERVAL:
            self.last_log_time = current_time
            elapsed = current_time - self.start_time
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.writer.writerow([timestamp, elapsed, temp, hum,  power, DESIRED_TEMPERATURE])
            self.file.flush()  # Guardar inmediatamente

    def close(self):
        self.file.close()

