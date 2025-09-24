import sys
import socket

# How many bytes is the word length?
WORD_LEN_SIZE = 2

def usage():
    print("usage: wordclient.py server port", file=sys.stderr)

def get_next_word_packet(s: socket.socket):
    """
    Return the next word packet from the stream.

    The word packet consists of the encoded word length followed by the
    UTF-8-encoded word.

    Returns None if there are no more words, i.e. the server has hung
    up.
    """

    packet_buffer: bytes = b""

    while len(packet_buffer) < 2:
        packet_buffer += s.recv(2)
        if not packet_buffer:
            return None

    length: int = int.from_bytes(packet_buffer, "big")
    full_packet_length: int = length + 2

    while len(packet_buffer) < full_packet_length:
        packet_buffer += s.recv(length)

        if not packet_buffer:
            raise Exception("Invalid number of bytes were sent.")

    return packet_buffer

def extract_word(word_packet: bytes) -> str:
    """
    Extract a word from a word packet.

    word_packet: a word packet consisting of the encoded word length
    followed by the UTF-8 word.

    Returns the word decoded as a string.
    """

    return word_packet[2:].decode()

def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s)

        if word_packet is None:
            break

        word = extract_word(word_packet)

        print(f"    {word}")

    s.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
