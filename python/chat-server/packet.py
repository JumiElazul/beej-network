from enum import Enum
import socket

MAX_RECEIVE: int = 1028

class PacketType(Enum):
    HELLO   = 0
    GOODBYE = 1
    CHAT    = 2
    EMOTE   = 3
    DM      = 4
    COMMAND = 5
    ERROR   = 6
    ABORT   = 7


class Packet:
    def __init__(self, type: PacketType, payload: str):
        self.type = type
        self.payload = payload


    def to_bytes(self) -> bytes:
        """
        Packet structure:
            Byte1   : PacketType enum
            Byte2-3 : Payload Length, 2 byte unsigned big-endian
            Byte4   : Payload bytes
        """
        payload_bytes = self.payload.encode()
        length = len(payload_bytes)

        if length > 0xFFFF:
            raise ValueError("Payload too large (max 65535 bytes)")

        return bytes([self.type.value]) + length.to_bytes(2, "big") + payload_bytes


    @classmethod
    def from_bytes(cls, data: bytes) -> 'Packet':
        if len(data) < 3:
            raise ValueError("Data too short to be a valid packet")

        type_byte = data[0]
        length = int.from_bytes(data[1:3], 'big')

        if len(data) < 3 + length:
            raise ValueError("Incomplete packet data")

        payload_bytes = data[3:3+length]
        payload_str = payload_bytes.decode('utf-8')
        packet_type = PacketType(type_byte)
        return cls(packet_type, payload_str)


def send_packet(sock: socket.socket, pkt: Packet):
    sock.sendall(pkt.to_bytes())


def receive_packet(sock: socket.socket, buffer: bytearray) -> Packet | None:
    data = sock.recv(MAX_RECEIVE)

    if not data:
        return None

    buffer.extend(data)

    if len(buffer) < 3:
        return None

    payload_length = int.from_bytes(buffer[1:3], "big")
    total_length = 3 + payload_length

    if len(buffer) < total_length:
        return None

    packet_bytes = buffer[:total_length]
    del buffer[:total_length]

    return Packet.from_bytes(bytes(packet_bytes))
