from twisted.internet import protocol, reactor

class VNCProtocol(protocol.Protocol):
    def connectionMade(self):
        print(f"Connection from {self.transport.getPeer()}")
        # Sende die RFB-Version (VNC-Version)
        self.transport.write(b"RFB 003.003\n")

    def dataReceived(self, data):
        print(f"Received data: {data}")
        if data.startswith(b"RFB"):
            # Handshake mit dem Client
            self.transport.write(b"\x01\x00")  # No authentication required

class VNCFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return VNCProtocol()

# Starte den Server auf Port 5900 (VNC-Standardport)
reactor.listenTCP(5900, VNCFactory())
reactor.run()
