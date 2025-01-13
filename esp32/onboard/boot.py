# BASE MICROPYTHON BOOT.PY-----------------------------------------------|  # noqa: INP001
# # This is all micropython code to be executed on the esp32 system level and doesn't require a __init__.py file

# This file is executed on every boot (including wake-boot from deep sleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
#------------------------------------------------------------------------|

import socket

import wifi_tools as wt
from AsyncManager import AsyncManager
from TCPHandler import TCPHandler
from UDPListener import UDPListener


def listen_for_search(UDPPort:int = 40000) -> None:
    """Listen for an incoming search message and respond with an ACK message.

    This function generates a UDP socket and then listens incoming SEARCH messages from another
    device on the network, likely the control server. The default port for broadcasting on the server
    side is 40000. This is meant as a troubleshooting function and should not be used in production.
    """

    # Create the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Lets the socket be reused
    sock.bind(("", UDPPort))

    print(f"Listening for search message on port {UDPPort}")

    try:
        while True:
            # Receive a message (max 1024 bytes)
            message, addr = sock.recvfrom(1024)
            print("Received message:", message.decode(), "from", addr)

            # Check if the message matches the search message
            if message.decode() == "SEARCH":
                print(f"SEARCH received from {addr}. Sending ACK.")
                ack_message = "ACK"

                # Send the ACK response back to the sender
                sock.sendto(ack_message.encode(), (addr[0], UDPPort))
                print("Sent Message:", ack_message)
    except KeyboardInterrupt:
        print("Stopping listener...")
    finally:
        sock.close()


UDPRequests = ("SEARCH", # Message received when server is searching for client sensors
               )

TCPRequests = ("SREAD", # Reads a single value from all sensors
               "CREAD", # Continuously reads data from all sensors until STOP received
               "STOP", # Stops continuous reading
               "STAT", # Returns number of sensors and types
               )

wlan = wt.connectWifi("Hous-fi", "nothomeless")

def main() -> None:
    udpListener = UDPListener(port=40000)
    tcpListener = TCPHandler(port=50000)
    server = AsyncManager(udpListener, tcpListener)
    server.run()
