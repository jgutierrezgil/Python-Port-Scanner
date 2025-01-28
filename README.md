# Python Port Scanner

This project is a port scanner written in Python. It allows you to scan open ports on a specific IP address.

## Requirements

- Python 3.x
- Additional libraries (see `requirements.txt`)

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/jgutierrezgil/Python-Port-Scanner.git
    ```
2. Navigate to the project directory:
    ```sh
    cd Python-Port-Scanner
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Setup

To set up the virtual environment, run the following commands:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Usage

Run the main script to scan ports:
```sh
python port_scanner.py <IP_ADDRESS>
```
Replace `<IP_ADDRESS>` with the IP address you want to scan.

## Running Tests

To run the tests, use the following command:
```bash
pytest
```

## Contributions

Contributions are welcome. Please open an issue or a pull request to discuss any major changes.

## License

This project is licensed under the GPL-3.0 License. See the `LICENSE` file for more details.
