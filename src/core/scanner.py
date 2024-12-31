import socket
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Union
import logging # Import logging module, used to log messages in the console

class PortScanner:
    
    # Constructor
    def __init__(self, timeout: float = 1, max_threads: int = 100):
        self.timeout = timeout # Timeout for socket connection
        self.max_threads = max_threads # Maximum number of threads
        self.logger = logging.getLogger(__name__) # Logger object
    
    def scan_port(self, target: str, port: int) -> Dict[str, Union[int, str, bool]]:
        """
        Scan an specific port in the given target.
        
        Args:
            target: IP or hostname to scan
            port: Number of port to scan
            
        Returns:
            Dictionary with the following keys:
                - port: Port number
                - state: State of the port (open/closed)
                - service: Service running in the port
                - error: Error message (if any)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # Create a socket object using IPv4 (AF_INET) and TCP (SOCK_STREAM)	
                sock.settimeout(self.timeout) # Set the timeout for the socket before leave the connection
                result = sock.connect_ex((target, port)) # Connect to the target and port, return 0 if the connection is successful
                is_open = result == 0 # Check if the connection is successful
                
                service = ""
                if is_open: # If the connection is successful, get the service name
                    try:
                        service = socket.getservbyport(port) # Get the service name by port
                    except:
                        service = "unknown"
                return { # Return the dictionary with the port, state, and service if the connection is successful
                    "port": port,
                    "state": "open" if is_open else "closed",
                    "service": service if is_open else "",
                }
                
        except socket.gaierror: # Handle the error of resolution of the hostname
            self.logger.error(f"Error of resolution of the hostname: {target}") # Log the error
            return {"port": port, "state": "error", "service": ""}
        except Exception as e: # Handle the generic error
            self.logger.error(f"Error scanning the port {port}: {str(e)}") # Log the error
            return {"port": port, "state": "error", "service": ""}

    def scan_port_range(self, target: str, start_port: int, end_port: int) -> List[Dict]:
        """
        Scan a range of ports using multithreading.
        
        Args:
            target: IP or hostname target IP o hostname objetivo
            start_port: Start port
            end_port: End Port
            
        Returns:
            List of results by port
        """
        ports = range(start_port, end_port + 1)
        results = []
            
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_port = {
                    executor.submit(self.scan_port, target, port): port 
                    for port in ports
                }
                
            for future in concurrent.futures.as_completed(future_to_port):
                    result = future.result()
                    results.append(result)
                    
                    # Log en tiempo real puertos abiertos
                    if result["state"] == "open":
                        self.logger.info(
                            f"Puerto {result['port']} abierto - "
                            f"Servicio: {result['service']}"
                        )
            
            return sorted(results, key=lambda x: x["port"])