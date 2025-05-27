#utils.py
import ustruct

def pack_float(value: float) -> bytes:
    """Convierte un float a 4 bytes (little-endian)."""
    return ustruct.pack('<f', value)

def i2c_communicate(i2c, slave_address: int, data_to_send: bytes = None, timeout_ms: int = 100) -> tuple[bool, bytes]:
    """
    Maneja comunicación bidireccional I2C:
    - Envía datos si el master los solicita.
    - Recibe datos si el master los envía.

    Args:
        i2c: Objeto I2C inicializado.
        slave_address: Dirección del esclavo (ej: 0x40).
        data_to_send: Bytes a enviar (opcional).
        timeout_ms: Tiempo de espera.

    Returns:
        Tuple[bool, bytes]: (éxito_en_envío, datos_recibidos).
    """
    try:
        # --- Envío de datos (si el master solicita) ---
        send_success = False
        received_data = None
        if data_to_send is not None and i2c.waitForRdReq(timeout=timeout_ms):
            i2c.write(data_to_send)
            send_success = True

        # --- Recepción de datos (si el master envía) ---
        received_data = None
        if i2c.waitForData(timeout=timeout_ms):
            received_data = i2c.read()

        return (send_success, received_data)

    except Exception as e:
        print(f"[ERROR I2C] {e}")
        return (False, None)
