from machine import mem32
import utime

class I2CSlave:
    def __init__(self, smbus, sda, scl, addr=0x42):
        self.addr = addr
        self.rx_buffer = bytearray()
        self.tx_buffer = bytearray()

        # Registros base para I2C0 e I2C1
        self.I2C_BASE = 0x40044000 if smbus == 0 else 0x40048000
        self.I2C_IC_CON = self.I2C_BASE + 0x00
        self.I2C_IC_TAR = self.I2C_BASE + 0x04
        self.I2C_IC_SAR = self.I2C_BASE + 0x08
        self.I2C_IC_DATA_CMD = self.I2C_BASE + 0x10
        self.I2C_IC_SS_SCL_HCNT = self.I2C_BASE + 0x14
        self.I2C_IC_SS_SCL_LCNT = self.I2C_BASE + 0x18
        self.I2C_IC_INTR_STAT = self.I2C_BASE + 0x2C
        self.I2C_IC_INTR_MASK = self.I2C_BASE + 0x30
        self.I2C_IC_CLR_INTR = self.I2C_BASE + 0x40
        self.I2C_IC_ENABLE = self.I2C_BASE + 0x6C
        self.I2C_IC_STATUS = self.I2C_BASE + 0x70

        self.init_slave()

    def init_slave(self):
        mem32[self.I2C_IC_ENABLE] = 0  # Deshabilitar I2C
        mem32[self.I2C_IC_SAR] = self.addr  # Dirección del esclavo
        mem32[self.I2C_IC_CON] = 0x61  # Slave mode, enable, 7-bit addr
        mem32[self.I2C_IC_INTR_MASK] = 0x15  # Habilitar interrupciones RX_FULL, RD_REQ y STOP_DET
        mem32[self.I2C_IC_ENABLE] = 1  # Habilitar I2C

    def _read_interrupts(self):
        return mem32[self.I2C_IC_INTR_STAT]

    def _clear_interrupts(self):
        mem32[self.I2C_IC_CLR_INTR]

    def _read_data_cmd(self):
        return mem32[self.I2C_IC_DATA_CMD] & 0xFF

    def _write_data_cmd(self, value):
        mem32[self.I2C_IC_DATA_CMD] = value & 0xFF

    def poll(self):
        """Debes llamar esta función frecuentemente en tu loop principal."""
        interrupts = self._read_interrupts()

        # Leer datos si el buffer está lleno
        if interrupts & (1 << 2):  # RX_FULL
            byte = self._read_data_cmd()
            self.rx_buffer.append(byte)

        # Maestro está leyendo: enviar siguiente byte
        if interrupts & (1 << 3):  # RD_REQ
            if self.tx_buffer:
                byte = self.tx_buffer.pop(0)
            else:
                byte = 0x00
            self._write_data_cmd(byte)

        # Comunicación terminada
        if interrupts & (1 << 9):  # STOP_DET
            self._clear_interrupts()
            return True  # Señal de fin de transacción
        return False

    def get_received_data(self):
        data = bytes(self.rx_buffer)
        self.rx_buffer = bytearray()
        return data

    def set_send_data(self, data):
        self.tx_buffer = bytearray(data)
