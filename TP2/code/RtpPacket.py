import sys
from time import time
HEADER_SIZE = 12

class RtpPacket:

    def __init__(self):
        self.header = bytearray(HEADER_SIZE)
        self.payload = b''

    def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
        """Encode the RTP packet with header fields and payload."""
        header = bytearray(HEADER_SIZE) 
        header[0] = (version << 6) | (padding << 5) | (extension << 4) | cc
        header[1] = (marker << 7) | pt
        header[2] = (seqnum >> 8) & 0xFF
        header[3] = seqnum & 0xFF
        header[4] = 0  # Timestamp não necessário, fixo a zero
        header[5] = 0
        header[6] = 0
        header[7] = 0
        header[8] = (ssrc >> 24) & 0xFF
        header[9] = (ssrc >> 16) & 0xFF
        header[10] = (ssrc >> 8) & 0xFF
        header[11] = ssrc & 0xFF

        self.header = header
        self.payload = payload

    def decode(self, byteStream):
        """Decode the RTP packet."""
        self.header = bytearray(byteStream[:HEADER_SIZE])
        self.payload = byteStream[HEADER_SIZE:]

    def version(self):
        """Return RTP version."""
        return int(self.header[0] >> 6)

    def seqNum(self):
        """Return sequence (frame) number."""
        return int(self.header[2] << 8 | self.header[3])

    def timestamp(self):
        """Return timestamp."""
        return int(self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7])

    def payloadType(self):
        """Return payload type."""
        return int(self.header[1] & 127)

    def getPayload(self):
        """Return payload."""
        return self.payload

    def getPacket(self):
        """Return RTP packet."""
        return self.header + self.payload