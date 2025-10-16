from enum import Enum
import socket

MAX_RECV: int = 1024

class PacketType(Enum):
    CONNECT = 1
    DISCONNECT = 3
    MESSAGE = 2


class Packet():
    def __init__(self, type: PacketType, payload: bytes):
        self.type = type
        self.payload = payload
        self.length = len(payload)


def create_packet(type: PacketType, payload: bytes):
    return Packet(type, payload)


def receive_packet(s: socket.socket) -> Packet:
    received: bytearray = bytearray()
    while True:
        received += s.recv(MAX_RECV)

        # Check first byte for packet type
        type: PacketType = PacketType(received[0])
        byte1, byte2 = received[1:3]
        payload_len = (byte1 << 8) | byte2

        while len(received) < (payload_len + 3):
            received += s.recv(MAX_RECV)

        return Packet(type, bytes(received[3:]))


def send_packet(s: socket.socket, packet: Packet):
    pass
