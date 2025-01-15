# BASE MICROPYTHON BOOT.PY-----------------------------------------------|  # noqa: INP001
# # This is all micropython code to be executed on the esp32 system level and doesn't require a __init__.py file

# This file is executed on every boot (including wake-boot from deep sleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
#------------------------------------------------------------------------|


import ujson  # type:ignore # noqa: I001# ujson and machine are micropython libraries

import wifi_tools as wt
from AsyncManager import AsyncManager
from TCPHandler import TCPHandler
from UDPListener import UDPListener

from sensors.Thermocouple import Thermocouple # type: ignore # don't need __init__ for micropython
from sensors.PressureTransducer import PressureTransducer # type: ignore
from sensors.LoadCell import LoadCell # type: ignore

CONFIG_FILE = "ESPConfig.json"

def readConfig(filePath: str):  # type: ignore  # noqa: ANN201
    try:
        with open(filePath, "r") as file:
            config = ujson.load(file)
            return config
    except Exception as e:
        print(f"Failed to read config file: {e}")
        return {}

def initializeFromConfig(config) -> list[Thermocouple | LoadCell | PressureTransducer]: # type: ignore  # noqa: ANN001 # Typing for the JSON object is impossible without the full Typing library
    """Initialize all devices and sensors from the config file.

    ADC index 0 indicates the sensor is connected directly to the ESP32. Any other index indicates
    connection to an external ADC.
    """
    sensors: list[Thermocouple | LoadCell | PressureTransducer] = []

    print(f"Initializing device: {config.get('deviceName', 'Unknown Device')}")
    deviceType = config.get("deviceType", "Unknown")

    if deviceType == "Sensor Monitor":
        sensorInfo = config.get("sensorInfo", {})

        for name, details in sensorInfo.get("thermocouples", {}).items():
            sensors.append(Thermocouple(name=name,
                                        ADCIndex=details["ADCIndex"],
                                        highPin=details["highPin"],
                                        lowPin=details["lowPin"],
                                        thermoType=details["type"],
                                        units=details["units"],
                                        ))

        for name, details in sensorInfo.get("pressureTransducers", {}).items():
            sensors.append(PressureTransducer(name=name,
                                              ADCIndex=details["ADCIndex"],
                                              pinNumber=details["pin"],
                                              maxPressure_PSI=details["maxPressure_PSI"],
                                              units=details["units"],
                                              ))

        for name, details in sensorInfo.get("loadCells", {}).items():
            sensors.append(LoadCell(name=name,
                                    ADCIndex=details["ADCIndex"],
                                    highPin=details["highPin"],
                                    lowPin=details["lowPin"],
                                    loadRating_N=details["loadRating_N"],
                                    excitation_V=details["excitation_V"],
                                    sensitivity_vV=details["sensitivity_vV"],
                                    units=details["units"],
                                    ))

        return sensors

    if deviceType == "Unknown":
        raise ValueError("Device type not specified in config file")

    return []


UDPRequests = ("SEARCH", # Message received when server is searching for client sensors
               )

TCPRequests = ("SREAD", # Reads a single value from all sensors
               "CREAD", # Continuously reads data from all sensors until STOP received
               "STOP", # Stops continuous reading
               "STAT", # Returns number of sensors and types
               )

wlan = wt.connectWifi("Hous-fi", "nothomeless")

config = readConfig(CONFIG_FILE)
sensors = initializeFromConfig(config)

def main() -> None:


    udpListener = UDPListener(port=40000)
    tcpListener = TCPHandler(port=50000)
    server = AsyncManager(udpListener, tcpListener)
    server.run()
