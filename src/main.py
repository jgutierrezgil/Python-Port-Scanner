import argparse
import sys
import logging
from datetime import datetime
from core.scanner import PortScanner

def setup_logging(verbose: bool):
    """Configure the logging system"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_ports(port_range: str) -> tuple:
    """Validate and parse the port range argument"""
    try:
        start, end = map(int, port_range.split('-'))
        if not (0 <= start <= 65535 and 0 <= end <= 65535):
            raise ValueError
        if start > end:
            start, end = end, start
        return start, end
    except ValueError:
        raise argparse.ArgumentTypeError(
            "The range of ports must be between 0 and 65535"
        )

def main():
    parser = argparse.ArgumentParser(
        description='Scanner ports with multithreading\n\n'
                   'Usage: python main.py <target> [-p port-range] [-t timeout] [--threads threads] [--tcp || --udp] [-v]\n'
                   'Example: python main.py localhost -p 80-443 -t 0.5 --threads 50 --tcp -v'
    )
    
    parser.add_argument(
        'target',
        help='IP or hostname to scan'
    )
    
    parser.add_argument(
        '-p', '--ports',
        default='1-1024',
        help='Ports range (Example: 1-1024)',
        type=validate_ports
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=1.0,
        help='Timeout for socket connection (default: 1.0 second)'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=100,
        help='Maximum number of threads (default: 100)'
    )
    
    parser.add_argument(
        '--tcp',
        action='store_true',
        help='Scan TCP ports (default)'
    )
    
    parser.add_argument(
        '--udp',
        action='store_true',
        help='Scan UDP ports'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose mode'
    )
        
    # Add the argument to the parser
    # You access to the arguments using the args object
    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        scanner = PortScanner(
            timeout=args.timeout,
            max_threads=args.threads
        )
        
        start_time = datetime.now()
        logger.info(f"Starting scan of {args.target}")
        logger.info(f"Ports range: {args.ports[0]}-{args.ports[1]}")
        logger.info(f"Protocol: {'TCP' if args.tcp else 'UDP'}")
        
        # Scan the ports using the function located in the scanner object
        results = scanner.scan_port_range(
            args.target,
            args.ports[0],
            args.ports[1],
            "udp" if args.udp else "tcp", # Protocol TCP or UDP. TCP by default
        )
        
        # Show the results
        open_ports = [r for r in results if r["state"] == "open"]
        scan_time = datetime.now() - start_time
        
        print("\nResults of the scan:")
        print(f"Target: {args.target}")
        print(f"Total time: {scan_time}")
        print(f"Scanned ports: {args.ports[1] - args.ports[0] + 1}")
        print(f"Openned ports: {len(open_ports)}")
        
        if open_ports:
            print("\nOpenned ports:")
            for result in open_ports:
                print(
                    f"Port {result['port']}\t"
                    f"open\t{result['service']}"
                )
                if args.tcp:
                    logger.info("/tcp")
                if args.udp:
                    logger.info("/udp")
                
    except KeyboardInterrupt:
        logger.info("Scan canceled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()