import pytest
from unittest.mock import patch
import sys
from main import validate_ports, setup_logging
import argparse
import logging

def test_validate_ports_valid_range():
    """Test valid port range validation"""
    assert validate_ports("80-443") == (80, 443)
    assert validate_ports("1-65535") == (1, 65535)
    # Test auto-correction of reversed range
    assert validate_ports("443-80") == (80, 443)

def test_validate_ports_invalid_range():
    """Test invalid port range validation"""
    with pytest.raises(argparse.ArgumentTypeError):
        validate_ports("70000-80000")  # Out of range
    with pytest.raises(argparse.ArgumentTypeError):
        validate_ports("abc-def")  # Invalid format
    with pytest.raises(argparse.ArgumentTypeError):
        validate_ports("-1-100")  # Negative port

def test_setup_logging_debug():
    """Test logging setup in debug mode"""
    setup_logging(True)
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG

def test_setup_logging_info():
    """Test logging setup in info mode"""
    setup_logging(False)
    logger = logging.getLogger()
    assert logger.level == logging.INFO

@pytest.fixture
def mock_args():
    """Fixture to create mock command line arguments"""
    class Args:
        target = "localhost"
        ports = (80, 443)
        timeout = 1.0
        threads = 100
        tcp = True
        udp = False
        verbose = False
    return Args()

@patch('argparse.ArgumentParser.parse_args')
def test_main_argument_parsing(mock_parse_args, mock_args):
    """Test command line argument parsing"""
    mock_parse_args.return_value = mock_args
    from main import main
    
    # This will raise SystemExit if argument parsing fails
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()
    assert pytest_wrapped_e.type == SystemExit

def test_main_keyboard_interrupt():
    """Test handling of keyboard interrupt"""
    with patch('main.PortScanner') as mock_scanner:
        mock_scanner.side_effect = KeyboardInterrupt()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main()
        assert pytest_wrapped_e.value.code == 1