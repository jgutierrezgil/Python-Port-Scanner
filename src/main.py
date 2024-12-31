import argparse
import sys
import logging
from datetime import datetime
from core.scanner import PortScanner

def setup_logging(verbose: bool):
    """Configura el sistema de logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_ports(port_range: str) -> tuple:
    """Valida y parsea el rango de puertos"""
    try:
        start, end = map(int, port_range.split('-'))
        if not (0 <= start <= 65535 and 0 <= end <= 65535):
            raise ValueError
        if start > end:
            start, end = end, start
        return start, end
    except ValueError:
        raise argparse.ArgumentTypeError(
            "El rango de puertos debe ser start-end (0-65535)"
        )

def main():
    parser = argparse.ArgumentParser(
        description='Scanner de puertos con multithreading'
    )
    
    parser.add_argument(
        'target',
        help='IP o hostname objetivo'
    )
    
    parser.add_argument(
        '-p', '--ports',
        default='1-1024',
        help='Rango de puertos (ejemplo: 1-1024)',
        type=validate_ports
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=1.0,
        help='Timeout para las conexiones (segundos)'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=100,
        help='Número máximo de threads'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verbose'
    )
    
    parser = argparse.ArgumentParser(
        description='Scanner ports with multithreading\n\n'
                   'Usage: python main.py <target> [-p port-range] [-t timeout] [--threads threads] [-v]\n'
                   'Example: python main.py localhost -p 80-443 -t 0.5 --threads 50 -v'
    )
        
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        scanner = PortScanner(
            timeout=args.timeout,
            max_threads=args.threads
        )
        
        start_time = datetime.now()
        logger.info(f"Iniciando escaneo de {args.target}")
        logger.info(f"Rango de puertos: {args.ports[0]}-{args.ports[1]}")
        
        results = scanner.scan_port_range(
            args.target,
            args.ports[0],
            args.ports[1]
        )
        
        # Mostrar resumen
        open_ports = [r for r in results if r["state"] == "open"]
        scan_time = datetime.now() - start_time
        
        print("\nResumen del escaneo:")
        print(f"Target: {args.target}")
        print(f"Tiempo total: {scan_time}")
        print(f"Puertos escaneados: {args.ports[1] - args.ports[0] + 1}")
        print(f"Puertos abiertos: {len(open_ports)}")
        
        if open_ports:
            print("\nPuertos abiertos:")
            for result in open_ports:
                print(
                    f"Puerto {result['port']}/tcp\t"
                    f"abierto\t{result['service']}"
                )
                
    except KeyboardInterrupt:
        logger.info("Escaneo interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()