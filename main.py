from machine import Pin, PWM
from bluetooth import BLE
import utime

# Configuración de BLE
ble = BLE()
ble.active(True)

# UUIDs del servicio y características BLE UART
UART_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

# Callback para recibir comandos
def on_rx(value):
    print(f"Comando recibido: {value}")
    process_command(value.decode('utf-8'))

# Procesar comandos recibidos
def process_command(command):
    if command == "FORWARD":
        set_motor1(50)
        set_motor2(50)
    elif command == "BACKWARD":
        set_motor1(-50)
        set_motor2(-50)
    elif command == "LEFT":
        set_motor1(-30)
        set_motor2(30)
    elif command == "RIGHT":
        set_motor1(30)
        set_motor2(-30)
    elif command == "STOP":
        stop_all()

# Publicar el servicio BLE UART
from ble_uart_peripheral import BLESimplePeripheral
ble_uart = BLESimplePeripheral(ble, UART_UUID, RX_CHAR_UUID, TX_CHAR_UUID)
ble_uart.on_write(on_rx)

# Configuración de motores
motor1_l_pwm = PWM(Pin(16))
motor1_r_pwm = PWM(Pin(17))
motor2_l_pwm = PWM(Pin(18))
motor2_r_pwm = PWM(Pin(19))
motor1_l_pwm.freq(1000)
motor1_r_pwm.freq(1000)
motor2_l_pwm.freq(1000)
motor2_r_pwm.freq(1000)

def stop_all():
    motor1_l_pwm.duty_u16(0)
    motor1_r_pwm.duty_u16(0)
    motor2_l_pwm.duty_u16(0)
    motor2_r_pwm.duty_u16(0)

def set_motor1(speed):
    if speed > 0:
        motor1_l_pwm.duty_u16(int(speed * 65535 / 100))
        motor1_r_pwm.duty_u16(0)
    elif speed < 0:
        motor1_l_pwm.duty_u16(0)
        motor1_r_pwm.duty_u16(int(-speed * 65535 / 100))
    else:
        stop_all()

def set_motor2(speed):
    if speed > 0:
        motor2_l_pwm.duty_u16(int(speed * 65535 / 100))
        motor2_r_pwm.duty_u16(0)
    elif speed < 0:
        motor2_l_pwm.duty_u16(0)
        motor2_r_pwm.duty_u16(int(-speed * 65535 / 100))
    else:
        stop_all()

# Bucle principal
print("Esperando comandos BLE...")
while True:
    utime.sleep(1)
