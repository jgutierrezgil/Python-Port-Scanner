import pytest
from unittest.mock import patch, MagicMock
from core.scanner import PortScanner

@pytest.fixture
def scanner():
    return PortScanner(timeout=0.1, max_threads=10)

def test_scanner_initialization():
    """Test scanner initialization with default values"""
    scanner = PortScanner()
    assert scanner.timeout == 1
    assert scanner.max_threads == 100

def test_scanner_custom_initialization():
    """Test scanner initialization with custom values"""
    scanner = PortScanner(timeout=2, max_threads=50)
    assert scanner.timeout == 2
    assert scanner.max_threads == 50

@pytest.mark.parametrize("protocol", ["tcp", "udp"])
def test_scan_valid_protocol(scanner, protocol):
    """Test scanning with valid protocols"""
    results = scanner.scan_port_range("localhost", 80, 81, protocol)
    assert isinstance(results, list)
    assert all(isinstance(r, dict) for r in results)
    assert all("port" in r and "state" in r and "service" in r for r in results)

def test_scan_invalid_protocol(scanner):
    """Test scanning with invalid protocol"""
    results = scanner.scan_port_range("localhost", 80, 81, "invalid")
    assert results == []

@patch('socket.socket')
def test_tcp_scan_open_port(mock_socket, scanner):
    """Test TCP scan when port is open"""
    # Configure mock
    mock_sock = MagicMock()
    mock_sock.connect_ex.return_value = 0
    mock_socket.return_value.__enter__.return_value = mock_sock
    
    result = scanner.scan_tcp_port("localhost", 80)
    assert result["state"] == "open"
    assert result["port"] == 80

@patch('socket.socket')
def test_tcp_scan_closed_port(mock_socket, scanner):
    """Test TCP scan when port is closed"""
    # Configure mock
    mock_sock = MagicMock()
    mock_sock.connect_ex.return_value = 1
    mock_socket.return_value.__enter__.return_value = mock_sock
    
    result = scanner.scan_tcp_port("localhost", 80)
    assert result["state"] == "closed"
    assert result["port"] == 80

def test_invalid_hostname(scanner):
    """Test scanning with invalid hostname"""
    result = scanner.scan_tcp_port("invalid.host.name", 80)
    assert result["state"] == "error"

def test_concurrent_scanning(scanner):
    """Test concurrent port scanning"""
    results = scanner.scan_port_range("localhost", 80, 85, "tcp")
    assert len(results) == 6  # Should have results for all ports
    assert all(isinstance(r, dict) for r in results)