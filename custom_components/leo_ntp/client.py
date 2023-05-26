"""LeoNTP API Client."""
from __future__ import annotations

import socket
import struct
import time

from .const import DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN
from .const import PORT

from .models import LeoNtpItem

from .utils import format_entity_name
from .utils import log_debug

class LeoNtpClient:
    """LeoNTP client."""

    def __init__(
        self,
        host: str | None = None,
        update_interval: int | None = None,
    ) -> None:
        """Initialize LeoNTP Client."""
        self.host = host
        self.update_interval = (
            update_interval if update_interval else DEFAULT_UPDATE_INTERVAL
        )


    def validate_server(self):
        """Validating LeoNTP connection."""

        log_debug(f"[LeoNtpClient|validate_server] Validating connection to {self.host}")

        data = {}
        ntp_server = self.host
        request_packet = bytearray(48)
        response_packet = bytearray(48)

        data["name"] = f"{ntp_server}:{PORT}"

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(3)  # Set a receive timeout of 3 seconds

            # Initialize the NTP request packet
            request_packet[0] = 4 << 3 | 7
            request_packet[1] = 0
            request_packet[2] = 0x10
            request_packet[3] = 1

            # Send the request packet to the NTP server
            sock.sendto(request_packet, (ntp_server, PORT))

            # Receive the response packet from the NTP server
            response_packet, _ = sock.recvfrom(48)

            serial_number = struct.unpack('<H', response_packet[42:44])[0]

            data["id"] = serial_number

        return data


    def fetch_data(self):
        """Fetch LeoNTP data."""

        log_debug(f"[LeoNtpClient|fetch_data] Fetching data for {self.host}")

        data = {}
        ntp_server = self.host
        request_packet = bytearray(48)
        response_packet = bytearray(48)

        # reference time (in seconds since 1900-01-01 00:00:00) for conversion from NTP time to system time
        TIME1970 = 2208988800

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(3)  # Set a receive timeout of 3 seconds

            # Initialize the NTP request packet
            request_packet[0] = 4 << 3 | 7
            request_packet[1] = 0
            request_packet[2] = 0x10
            request_packet[3] = 1

            # Send the request packet to the NTP server
            sock.sendto(request_packet, (ntp_server, PORT))

            # Receive the response packet from the NTP server
            response_packet, _ = sock.recvfrom(48)

            ref_ts0          = (struct.unpack('<I', response_packet[16:20])[0]) / 4294967296.0  # fractional part of the NTP timestamp
            ref_ts1          = struct.unpack('<I', response_packet[20:24])[0]                   # full seconds of NTP timestamp
            uptime           = struct.unpack('<I', response_packet[24:28])[0]
            ntp_served 	     = struct.unpack('<I', response_packet[28:32])[0]
            cmd_served       = struct.unpack('<I', response_packet[32:36])[0]
            gps_lock_time    = struct.unpack('<I', response_packet[36:40])[0]
            gps_flags        = response_packet[40]
            gps_satellites   = response_packet[41]
            serial_number    = struct.unpack('<H', response_packet[42:44])[0]
            firmware_version = struct.unpack('<I', response_packet[44:48])[0]

            id = serial_number
            device_model = DOMAIN.title()
            device_key = format_entity_name(f"{device_model} {id}")
            device_name = f"{ntp_server}:{PORT}"

            key = format_entity_name(f"{id} id")
            data[key] = LeoNtpItem(
                name = "NTP Requests",
                key = key,
                type = "requests_served",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = ntp_served,
            )

            # actual statistics received from the server
            t = time.gmtime(ref_ts1 - TIME1970)
            print("UTC time: %d-%02d-%02d %02d:%02d:%02.0f" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec + ref_ts0))
            print("NTP time: %02.0f" % (ref_ts1 + ref_ts0))

            print("Average load since restart: %02.0f requests per second" % (1.0 * NTP_served / uptime))
            print("NTP requests served:", NTP_served)
            print("Mode 6 requests served:", CMD_served)
            print("Uptime:", uptime, "seconds (", uptime/86400, "days )")
            print("GPS lock time:", lock_time, "seconds (", lock_time/86400, "days )")
            print("GPS flags:", flags)
            print("Active satellites:", numSV)
            print("Firmware version: %x.%02x" % (FW_ver>>8, FW_ver&0xFF))
            print("Serial number:", ser_num)

        return data
# id, name
