import socket


class UDPListener:
    def __init__(self, port : int = 40000 ) -> None:
        self.port = port
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # AF_INET = IPV4, DGRAM = UDP
        self.udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows rebinding to the same port. Handy if not clean shutdown of listener

        self.searcherPort = 30000 # Port that the searcher listens on for UDP broadcasts

        self.udpSocket.bind(("", self.port))
        print("UDP Listener initialized on port", self.port)

    def handleMessage(self, data: bytes, address: str, activeServerPort: int) -> None:  # type: ignore # noqa: ANN001 # createNewServerCallback is a function is a function. No typing module in micropython to specify "Callable"
        if data.decode("utf-8") == "SEARCH":
            response = f"ACK:{activeServerPort}" # Respond with the active TCP server port number
            self.udpSocket.sendto(response.encode("utf-8"), (address[0], self.searcherPort))
            print(f"Sent ACK with active server port {activeServerPort} to {address[0], self.searcherPort}")
