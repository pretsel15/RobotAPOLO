import bluetooth
from micropython import const
import struct

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_WRITE)

_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)

class BLESimplePeripheral:
    def __init__(self, ble, name="PicoW_UART"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._rx_buffer = bytearray()

        self._handlers = {}
        self._payload = self._advertising_payload(name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()

    def _irq(self, event, data):
        if event == bluetooth.IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == bluetooth.IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            self._advertise()
        elif event == bluetooth.IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._rx_handle:
                self._rx_buffer = self._ble.gatts_read(self._rx_handle)
                if "on_write" in self._handlers:
                    self._handlers["on_write"](self._rx_buffer)

    def on_write(self, handler):
        self._handlers["on_write"] = handler

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    @staticmethod
    def _advertising_payload(name=None, appearance=0):
        payload = bytearray()

        def _append(adv_type, value):
            payload.extend(struct.pack("BB", len(value) + 1, adv_type))
            payload.extend(value)

        if name:
            _append(0x09, name.encode())
        _append(0x19, struct.pack("<H", appearance))

        return payload
