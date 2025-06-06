import json
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from libqretprop.ESPObjects.SensorMonitor.SensorMonitor import SensorMonitor

class ESPDevice:
    """A top level class representing the configuration of a connected ESP32 device.

    Currently, the only supported device (subclass) is the Sensor Monitor.  To
    define a device call the fromConfigBytes method and pass the byte stream of
    the configuration file received from the device. This will return an object
    of the appropriate type, assuming the device type in the configuration file
    is recognized.

    Parameters
    ----------
        jsonConfig (dict): The JSON configuration of the device, streamed back from the ESP32 on initial connection.
        address (str): The IP address of the ESP32 device.

    """
    def __init__(self,
                 jsonConfig: dict[str, Any],
                 address: str,
                 ) -> None:

        self.jsonConfig = jsonConfig

        self.name = jsonConfig["deviceName"]
        self.type = jsonConfig["deviceType"]
        self.address = address

    def sendCommand(self, command: str) -> None:
        """Send a command to the device.

        Parameters
        ----------
        command : str
            The command to send to the device.

        """
        raise NotImplementedError("This method should be implemented in subclasses.")




    @staticmethod
    def fromConfigBytes(configBytes: bytes, address: str) -> "SensorMonitor": # Delay evaluation of SensorMonitor to avoid circular imports
        configJson = json.loads(configBytes.decode("utf-8"))
        deviceType = configJson["deviceType"]

        if deviceType in {"Sensor Monitor", "Simulated Sensor Monitor"}:
            # To avoid circular imports, import the SensorMonitor class only within the scope of this function
            from libqretprop.ESPObjects.SensorMonitor.SensorMonitor import SensorMonitor

            return SensorMonitor(configJson, address)
        else:
            err = f"Device type {deviceType} not recognized."
            raise ValueError(err)

