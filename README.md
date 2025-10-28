[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/coreyhines/config-tool)

# config-tool

A powerful toolkit for analyzing and managing Arista EOS device configurations at scale. Extract common configuration patterns across your network and generate CloudVision Portal configlets for consistent container-level application.

## 🚀 Features

- **Configuration Analysis**: Find common configuration stanzas across multiple devices
- **Automated Config Collection**: Pull configurations from EOS devices via eAPI
- **CloudVision Integration**: Generate configlets for container-level application
- **High Performance**: Choose between Python for flexibility or Rust for speed
- **Development Environments**: Support for both VS Code devcontainers and DevPod

## 📋 Prerequisites

- Python 3.12+ for Python implementation
- Rust toolchain (optional) for high-performance implementation
- Valid EOS device credentials with eAPI access enabled
- One of:
  - VS Code with Dev Containers extension
  - DevPod
  - Local Python/Rust environment

## 🛠 Installation

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/coreyhines/config-tool.git
   cd config-tool
   ```

2. Choose your development environment:
   ```bash
   # Option 1: VS Code Devcontainer
   code .  # Then click "Reopen in Container"

   # Option 2: DevPod
   devpod up

   # Option 3: Local Installation
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pre-commit install
   ```

For detailed setup instructions, see the [Build Guide](./docs/BUILD.md).

## 🔧 Usage

### Configuration Analysis (config-tool)

Analyze configuration patterns across multiple EOS devices:

```bash
./config-tool.py --directory /path/to/configs \
                 --mask description \
                 --count 3 \
                 --absolute common
```

Options:
- `--directory PATH`: Location of EOS configuration files
- `--mask STRING`: Ignore specific elements during comparison (e.g., descriptions)
- `--count #`: Threshold for considering a stanza "common" (default: 3)
- `--absolute`: Specify output type
  - `common`: Show only stanzas present in all configs
  - `specific`: Show unique stanzas

#### Example Output

When analyzing configurations with `./config-tool.py -d ./configs -c 8`, the tool identifies common configuration patterns:

```
↓ SEEN ->(10/11)<- TIMES ↓
!
aaa group server radius RADCLIENT
   server rad.example.com vrf mgmt
!
↑ SEEN ->(10/11)<- TIMES ↑

↓ SEEN ->(8/11)<- TIMES ↓
!
aaa authentication login default group RADCLIENT local
aaa authentication login console local
!
↑ SEEN ->(8/11)<- TIMES ↑

↓ SEEN ->(10/11)<- TIMES ↓
!
alias conint sh interface | I connected
alias dump bash tcpdump -i %1
alias findmac bash sudo ip netns exec ns-mgmt /mnt/flash/Scripts/locateMac.py %1
alias routeage bash echo 'show ip route' | cliribd
alias scp bash sudo ip netns exec ns-mgmt scp
alias senz show interface counter error | nz
alias shinz show int counters errors | nz
alias shmc show int | awk '/^[A-Z]/ { intf = $1 } /, address is/ { print intf, $6 }'
alias shvxaddr show vxlan address-table
alias snz show interface counter | nz
alias spd show port-channel %1 detail all
alias sqnz show interface counter queue | nz
alias srnz show interface counter rate | nz
!
↑ SEEN ->(10/11)<- TIMES ↑

↓ SEEN ->(10/11)<- TIMES ↓
!
event-handler config-versioning
   trigger on-startup-config
   action bash FN=/mnt/flash/startup-config; LFN="`ls -1 $FN.*-* | tail -n 1`"; if [ -z "$LFN" -o -n "`diff -I 'last modified' $FN $LFN`" ]; then cp $FN $FN.`date +%Y%m%d-%H%M%S`; ls -1r $FN.*-* | tail -n +11 | xargs -I % rm %; fi
   delay 0
!
↑ SEEN ->(10/11)<- TIMES ↑

↓ SEEN ->(8/11)<- TIMES ↓
!
interface Loopback300
   description ipfix-source
   ip address 10.10.10.10/32
!
↑ SEEN ->(8/11)<- TIMES ↑
```

This output shows:
- **Common AAA configurations** found across 8-10 devices
- **Standard aliases** used for network troubleshooting
- **Event handlers** for configuration versioning
- **Loopback interfaces** with consistent addressing
- **Authentication methods** shared across the network

The tool helps identify configuration patterns that can be standardized into CloudVision Portal configlets for consistent deployment.

### Configuration Collection (confgrabber)

Pull configurations from live EOS devices:

```bash
./confgrabber.py --user admin \
                 --passwd 'secret' \
                 --file switches.txt \
                 --directory ./configs/ \
                 --sanitized \
                 --workers 10
```

Options:
- `--user STRING`: EOS device username
- `--passwd STRING`: EOS device password
- `--file PATH`: File containing list of switch hostnames/IPs
- `--directory PATH`: Output directory for configurations
- `--sanitized`: Get sanitized configs (removes sensitive data)
- `--workers N`: Maximum number of parallel workers (default: CPU count)

### Development Setup

The project includes a complete development environment with:

1. **Code Quality Tools**:
   - Black for code formatting
   - Ruff for linting and import sorting
   - Pre-commit hooks for consistent code quality

2. **Testing**:
   - pytest for unit testing
   - pytest-cov for coverage reporting

3. **Container Support**:
   - VS Code devcontainer configuration
   - DevPod support
   - Fedora-based development environment

4. **Dependencies**:
   - Core: jsonrpclib-pelix, ping3
   - Development: black, ruff, pytest, pre-commit
   - All versions pinned for reproducibility

## ⚡ Performance Optimization

### Python vs Rust Implementation

Choose based on your needs:

| Feature | Python | Rust |
|---------|--------|------|
| Setup Complexity | Simple | Requires compilation |
| Memory Usage | Higher | Lower |
| Processing Speed | Good | Excellent |
| Parallel Processing | ThreadPoolExecutor | Full concurrency |
| Best For | Development, small deployments | Production, large scale |

See [RUST_USAGE.md](./RUST_USAGE.md) for Rust-specific features and usage.

## 🔒 Security

- Credentials are never stored in configuration files
- Support for environment variables for sensitive data
- Secure eAPI communication over HTTPS
- Optional sanitized config collection
- SSL verification (can be disabled if needed)
- Exponential backoff for failed attempts

## 🛠 Development

### Development Environments

1. **VS Code Devcontainer**:
   - Python 3.12 environment
   - Pre-configured linting and formatting
   - Rust toolchain (optional)
   - Git integration
   - Debugging support

2. **DevPod**:
   - Podman support
   - Consistent environment
   - IDE-agnostic
   - Faster container startup

See [Build Guide](./docs/BUILD.md) for detailed development setup instructions.

## 📚 Documentation

- [Build Guide](./docs/BUILD.md): Detailed setup instructions
- [RUST_USAGE.md](./RUST_USAGE.md): Rust implementation details
- [API Documentation](./docs/API.md): eAPI integration details
- [Contributing Guide](./CONTRIBUTING.md): Development guidelines

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) for details on:
- Code style (Black + Ruff)
- Development process
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Arista Networks for EOS and CloudVision
- The Rust and Python communities
- All contributors to this project

# EOS Configuration Grabber

A Python script to download configurations from multiple EOS devices in parallel using eAPI.

## Features

- Parallel configuration downloads from multiple devices
- Support for both HTTP and HTTPS eAPI
- SSL certificate verification bypass
- Environment variable support for credentials
- Configurable worker threads
- Sanitized configuration option
- Port availability checking
- Retry mechanism with exponential backoff

## Installation

Install required packages:

```bash
pip install jsonrpclib-pelix requests
```

## Usage

### Command Line Arguments

```bash
python3 confgrabber.py -u username -p password -f hosts.txt -d configs/
```

### Arguments

- `-u, --user`: Username (or set `EAPI_USER` environment variable)
- `-p, --passwd`: Password (or set `EAPI_PASS` environment variable)
- `-f, --file`: File containing list of hostnames (required)
- `-d, --directory`: Output directory for configs (default: current directory)
- `-s, --sanitized`: Get sanitized configuration
- `-w, --workers`: Maximum number of worker threads
- `--skip-check`: Skip port availability check
- `-r, --scan-result`: Scan result file for protocol/port mapping

### Environment Variables

You can set credentials using environment variables instead of command line arguments:

```bash
export EAPI_USER=your_username
export EAPI_PASS=your_password
python3 confgrabber.py -f hosts.txt -d configs/
```

### .env File Support

Create a `.env` file in the same directory as the script:

```bash
# Copy the example file
cp env.example .env

# Edit .env with your credentials
EAPI_USER=your_username
EAPI_PASS=your_password
```

The script will automatically load the `.env` file if it exists.

## Examples

### Basic Usage
```bash
python3 confgrabber.py -u admin -p mypassword -f devices.txt -d configs/
```

### Using Environment Variables
```bash
export EAPI_USER=admin
export EAPI_PASS=mypassword
python3 confgrabber.py -f devices.txt -d configs/
```

### With Sanitized Configs
```bash
python3 confgrabber.py -u admin -p mypassword -f devices.txt -d configs/ -s
```

### With Custom Worker Count
```bash
python3 confgrabber.py -u admin -p mypassword -f devices.txt -d configs/ -w 10
```

## Input File Format

The hosts file should contain one hostname per line:

```
switch1.example.com
switch2.example.com
switch3.example.com
```

## Output

Configurations are saved as text files named after each hostname in the specified directory:

```
configs/
├── switch1.example.com.txt
├── switch2.example.com.txt
└── switch3.example.com.txt
```

## Recent Fixes

- Fixed password encoding issue that was causing 400 Bad Request errors
- Removed URL encoding of passwords (jsonrpclib handles this internally)
- Added environment variable support for credentials
- Added .env file support
- Simplified SSL verification using global context
- Fixed type annotations and linter errors

## Troubleshooting

### 400 Bad Request Errors
If you're getting 400 Bad Request errors, ensure you're using the latest version of the script. The password encoding issue has been fixed.

### Authentication Failures
- Verify username and password are correct
- Ensure eAPI is enabled on the devices
- Check that the devices are reachable on the expected ports (443 for HTTPS, 80 for HTTP)

### Connection Issues
- Use `--skip-check` to bypass port availability checking
- Verify network connectivity to the devices
- Check firewall rules
