import sys
import socket

# How many bytes is the word length?
WORD_LEN_SIZE = 2

def usage():
    print("usage: wordclient.py <server> <port> <bytes_per_recv>", file=sys.stderr)

packet_buffer = b''

def get_next_word_packet(s: socket.socket, recv_amnt: int) -> bytes | None:
    """
    Return the next word packet from the stream.

    The word packet consists of the encoded word length followed by the
    UTF-8-encoded word.

    Returns None if there are no more words, i.e. the server has hung
    up.
    """

    global packet_buffer

    def fill_buffer(need: int) -> bool:
        """
        Attemps to fill the global packet_buffer with 'need' bytes.

        Returns True if it was successful, otherwise False.
        """
        global packet_buffer

        while len(packet_buffer) < need:
            chunk = s.recv(recv_amnt)

            if chunk == b"":
                return False

            packet_buffer += chunk
        return True

    if not fill_buffer(WORD_LEN_SIZE):
        if len(packet_buffer) == 0:
            return None

        raise ValueError("Bytestream ended mid packet. (missing length header)")

    n = int.from_bytes(packet_buffer[:WORD_LEN_SIZE], "big")
    total_needed: int = WORD_LEN_SIZE + n

    if not fill_buffer(total_needed):
        raise ValueError("Stream ended mid-packet (incomplete payload)")

    packet = packet_buffer[:total_needed]
    packet_buffer = packet_buffer[total_needed:]
    return packet

def extract_word(word_packet: bytes) -> str:
    """
    Extract a word from a word packet.

    word_packet: a word packet consisting of the encoded word length
    followed by the UTF-8 word.

    Returns the word decoded as a string.
    """

    return word_packet[2:].decode()

# Do not modify:

def main(argv):
    try:
        host = argv[1]
        port = int(argv[2])
        recv_amnt = int(argv[3])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    print("Getting words:")

    while True:
        word_packet = get_next_word_packet(s, recv_amnt)

        if word_packet is None:
            break

        word = extract_word(word_packet)

        print(f"    {word}")

    s.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
