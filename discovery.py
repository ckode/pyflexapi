from socket import *
import time

class FlexRadioDiscoveryPacket:
    """
    class FlexRadioDiscoveryPacket

    FlexRadioDiscoveryPacket is an encapsulation of the data carried
    in Flex Radio's discovery protocol UDP packet.

    This object should generally only be created by the
    FlexRadioDiscoveryListener class and the object returned to your
    application.  The attributes themselves can be accessed directly.

    Parameters:
        packet_value (dict)  A dictionary containing the key / value pair provided by the packet

    Methods:
        None: Only private methods

    Attributes:
        self.requires_additional_license
        self.nickname
        self.version
        self.discovery_protocol_version
        self.inuse_ip
        self.model
        self.max_licensed_version
        self.serial
        self.inuse_host
        self.port
        self.radio_license_id
        self.ip
        self.status
        self.callsign
        self.fpc_mac

    """
    def __init__(self, packet_values):
        self.requires_additional_license = None
        self.nickname = None
        self.version = None
        self.discovery_protocol_version = None
        self.inuse_ip = None
        self.model = None
        self.max_licensed_version = None
        self.serial = None
        self.inuse_host = None
        self.port = None
        self.radio_license_id = None
        self.ip = None
        self.status = None
        self.callsign = None
        self.fpc_mac = None

        self._assignValues(packet_values)


    def _assignValues(self, packet_values):
        """
        obj._assignValues(self, packet_values)

        Assign values found in discovery packet to class variables
        """
        obj_var_list = [item for item in dir(self) if not item.startswith("__")]
        for k, v in packet_values.items():
            if k in obj_var_list:
                setattr(self, k, v)
            else:
                print("New values found in discovery packet that do not match DiscoveryPacket class")
                print("Attribute: %s - Value: %s" % (k, v))


class FlexRadioDiscoveryListener:
    """
    class FlexRadioDiscoveryListener

    Example:
        listener = FlexRadioDiscoveryListener(bind_ip, port, timeout)
        packet = listener.getDiscoveryPacket()

     Parameters:
         bind_ip: (str): An ip address to bind to. Default = '0.0.0.0'
         port: (INT): The port number to listen on.  Default = 4992
         timeout: (INT): An integer in seconds.  Default = 3

    Attributes:
         None

    Methods:
         getDiscoveryPacket()

     FlexRadioDiscoveryListener listens for Flex Radio's discovery
     UDP packets.  This packets are encapsulated in FlexRadioDiscoveryPacket
     objects and returned for evaluation. Each time a discovery packet is wanted,
     obj.getDiscoveryPacket() must be called.
    """
    def __init__(self, ipaddr='0.0.0.0', port=4992, timeout=3):
        self._sock = socket(AF_INET, SOCK_DGRAM)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self._sock.settimeout(timeout)
        self._sock.bind((ipaddr, port))
        self._packet_values = {}

    def getDiscoveryPacket(self):
        """
        getDiscoveryPacket()

        Example:
            listener = FlexRadioDiscoveryListener(bind_ip, port, timeout)
            packet = listener.getDiscoveryPacket()

        :return: packet ~ Object of type FlexRadioDiscoveryPacket()

        Parameters:
            None

        Attributes:
            None

        This method returns an object of type FlexRadioDiscoveryPacket() if a
        UDP discovery packet was found.  Otherwise, it returns None.
        """
        try:
            packet = self._sock.recvfrom(1024)
        except timeout as msg:
            return None

        # Trim UDP header, then split settings data up into a list
        plist = str(packet[0][28:]).split(" ")
        for item in plist:
            key, value = item.split("=")
            # Remove the byte type b' from the beginning of the first key name
            if "b'" in key:
                key = str(key.replace("b'", ""))
            self._packet_values[key] = value

        return FlexRadioDiscoveryPacket(self._packet_values)



if __name__ == "__main__":
    listener = FlexRadioDiscoveryListener()
    while 1:
        packet = listener.getDiscoveryPacket()
        if packet:
            print("******************************************")
            print("Radio found: %s" % (packet.model,))
            print("Radio Serial Number: %s" % (packet.serial,))
            print("Radio License: %s" % (packet.radio_license_id,))
            print("Radio Licensed for SmartSDR version: %s" % (packet.max_licensed_version,))
            print("Radio Registered to: %s" % (packet.callsign,))
            print("Software version: %s" % (packet.version,))
            print("Radio IP Address: %s" % (packet.ip,))
            if packet.status == "Available":
                print("Radio is %s" % (packet.status,))
            else:
                print("Radio is in use")
                print("Connected IP Address: %s" %(packet.inuse_ip,))
                print("Connected Hostname: %s" % (packet.inuse_host,))
            print("*******************************************\n\n")
            packet = None
        else:
            print("No packet found")
        time.sleep(1)



