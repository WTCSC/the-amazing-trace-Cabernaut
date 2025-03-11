# Traceroute Analyzer

## Overview
This Python script executes a traceroute to a given destination, parses the results, and visualizes the average round-trip time (RTT) per hop.

## Features
- Runs a **traceroute** command using ICMP (`-I` flag).
- Parses the output to extract **hop numbers, IP addresses, hostnames, and RTTs**.
- Handles missing data (`*` for timeouts).
- Visualizes RTTs per hop using **matplotlib**.

## Requirements
- Python 3.x
- `matplotlib` (install with `pip install matplotlib`)
- A system with `traceroute` installed (Linux/macOS)

## Installation
1. Clone the repository or copy the script.
2. Install dependencies:
   ```sh
   pip install matplotlib
   ```

## Usage
Run the script with a destination domain/IP:

```python
destination = "google.com"
output = execute_traceroute(destination)
parsed_data = parse_traceroute(output)
```

### Example Output:
```sh
traceroute to google.com (142.250.185.238), 30 hops max, 60 byte packets
1  router.local (192.168.1.1)  1.123 ms  1.234 ms  1.456 ms
2  * * *
3  10.10.10.1 (10.10.10.1)  15.678 ms  16.123 ms  14.890 ms
...
```

A **graph of average RTT per hop** will be displayed.

## Notes
- If `traceroute` is not found, ensure it is installed:  
  - **Ubuntu/Debian**: `sudo apt install traceroute`
  - **macOS**: Installed by default.
  - **Windows**: Use `tracert` instead.
