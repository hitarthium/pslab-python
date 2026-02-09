"""
MockHandler for PSLab.

This module provides a software simulation of the PSLab hardware interface.
It allows developers to test signal processing and communication logic
without physical hardware by injecting custom response data.
"""

import logging
import struct
from typing import Dict, Optional, Union

class MockHandler:
    """
    A mock communication handler that simulates the PSLab hardware.
    """

    def __init__(self, port: Optional[str] = None):
        self.connected = False
        self.port = port or "MOCK_PORT"
        self.response_map: Dict[bytes, bytes] = {}
        self.read_buffer = bytearray()
        self.logger = logging.getLogger(__name__)

    def open(self, port: Optional[str] = None) -> None:
        """
        Simulate opening the connection.
        
        Args:
            port (str, optional): The port to connect to. Updates the handler's port if provided.
        """
        if port:
            self.port = port
        self.connected = True
        self.logger.info(f"MockHandler connected on {self.port}")
    def close(self) -> None:
        self.connected = False
        self.read_buffer.clear()
        self.logger.info("MockHandler disconnected.")

    def write(self, data: bytes) -> int:
        if not self.connected:
            raise RuntimeError("Attempted to write to closed MockHandler.")

        # Check for registered responses
        match_found = False
        for command, response in self.response_map.items():
            if data.startswith(command):
                self.read_buffer.extend(response)
                match_found = True
                break
        
        if not match_found:
            self.logger.debug(f"Write: {data.hex()} (No specific response mapped)")

        return len(data)

    def read(self, size: int = 1) -> bytes:
        """
        Read bytes from the mock buffer.
        
        Parameters
        ----------
        size : int
            Number of bytes to read.
            
        Returns
        -------
        bytes
            The data read from the buffer.
        """
        if not self.connected:
            raise RuntimeError("Attempted to read from closed MockHandler.")

        available = len(self.read_buffer)
        if available < size:
            self.logger.warning(f"MockHandler: Requested {size} bytes, but only {available} available.")
            # Return what we have, then empty the buffer
            data = self.read_buffer[:]
            self.read_buffer.clear()
            return bytes(data)

        data = self.read_buffer[:size]
        self.read_buffer = self.read_buffer[size:]
        return bytes(data)

    def get_ack(self) -> int:
        """
        Simulate receiving an acknowledgement from the device.
        
        Returns
        -------
        int
            ACK value (0x01).
        """
        return 0x01

        if len(self.read_buffer) < size:
            self.logger.warning(f"MockHandler: Requested {size} bytes, but only {len(self.read_buffer)} available.")
            # Return what we have, then empty bytes
            data = self.read_buffer[:]
            self.read_buffer.clear()
            return bytes(data)

        data = self.read_buffer[:size]
        self.read_buffer = self.read_buffer[size:]
        return bytes(data)

    def clear_buffer(self) -> None:
        self.read_buffer.clear()

    # --- Interface Compatibility Methods ---

    def send_byte(self, val: Union[int, bytes]) -> None:
        """
        Sends a single byte to the device.
        Handles both integer (0-255) and single-byte bytes objects.
        """
        if isinstance(val, int):
            self.write(bytes([val]))
        elif isinstance(val, bytes):
            self.write(val)
        else:
            raise TypeError(f"send_byte expects int or bytes, got {type(val)}")

    def send_int(self, val: int) -> None:
        """Sends a 16-bit integer to the device."""
        self.write(struct.pack('<H', val)) # Little-endian unsigned short

    def read_byte(self) -> int:
        """Reads a single byte and returns it as an integer."""
        data = self.read(1)
        if not data:
            return 0 
        return data[0]
    
    def read_int(self) -> int:
        """Reads two bytes and interprets them as a 16-bit integer."""
        data = self.read(2)
        if len(data) < 2:
            return 0
        return struct.unpack('<H', data)[0]

    def get_ack(self) -> bool:
        """Simulates receiving an acknowledgement from the device."""
        return True

    # --- Developer Control Methods ---

    def register_response(self, command: bytes, response: bytes) -> None:
        self.response_map[command] = response

    def inject_data(self, data: bytes) -> None:
        self.read_buffer.extend(data)