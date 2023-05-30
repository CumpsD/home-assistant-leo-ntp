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
        """Validate LeoNTP connection."""

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

            data["id"] = f"{serial_number}"

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
            # cmd_served       = struct.unpack('<I', response_packet[32:36])[0]
            gps_lock_time    = struct.unpack('<I', response_packet[36:40])[0]
            gps_flags        = response_packet[40]
            gps_satellites   = response_packet[41]
            serial_number    = struct.unpack('<H', response_packet[42:44])[0]
            firmware_version = struct.unpack('<I', response_packet[44:48])[0]

            gps_lock = (gps_flags & 1) == 1;

            id = serial_number
            device_model = DOMAIN.title()
            device_key = format_entity_name(f"{device_model} {id}")
            device_name = f"{ntp_server}:{PORT}"

            t = time.gmtime(ref_ts1 - TIME1970)
            key = format_entity_name(f"{id} utc_time")
            data[key] = LeoNtpItem(
                name = "UTC Time",
                key = key,
                type = "utc_time",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = f"{t.tm_year}-{t.tm_mon:02d}-{t.tm_mday:02d} {t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec + ref_ts0:02.0f}",
            )

            key = format_entity_name(f"{id} ntp_time")
            data[key] = LeoNtpItem(
                name = "NTP Time",
                key = key,
                type = "ntp_time",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = f"{ref_ts1 + ref_ts0:02.0f}",
            )

            key = format_entity_name(f"{id} requests_served")
            data[key] = LeoNtpItem(
                name = "NTP Requests",
                key = key,
                type = "requests_served",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = ntp_served,
            )

            key = format_entity_name(f"{id} uptime")
            data[key] = LeoNtpItem(
                name = "Uptime",
                key = key,
                type = "uptime",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = uptime,
            )

            key = format_entity_name(f"{id} gps_lock")
            data[key] = LeoNtpItem(
                name = "GPS Lock",
                key = key,
                type = "gps_lock",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = gps_lock,
            )

            key = format_entity_name(f"{id} gps_lock_time")
            data[key] = LeoNtpItem(
                name = "GPS Lock Time",
                key = key,
                type = "gps_lock_time",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = gps_lock_time,
            )

            key = format_entity_name(f"{id} gps_flags")
            data[key] = LeoNtpItem(
                name = "GPS Flags",
                key = key,
                type = "gps_flags",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = gps_flags,
            )

            key = format_entity_name(f"{id} satellites")
            data[key] = LeoNtpItem(
                name = "GPS Satellites",
                key = key,
                type = "satellites",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = gps_satellites,
            )

            key = format_entity_name(f"{id} firmware_version")
            data[key] = LeoNtpItem(
                name = "Firmware Version",
                key = key,
                type = "firmware_version",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = f"{firmware_version >> 8:x}.{firmware_version & 0xFF:02x}",
            )

            key = format_entity_name(f"{id} serial_number")
            data[key] = LeoNtpItem(
                name = "Serial Number",
                key = key,
                type = "serial_number",
                device_key = device_key,
                device_name = device_name,
                device_model = device_model,
                state = serial_number,
            )

        return data

