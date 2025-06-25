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
- Valid EOS device credentials
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
   pip install -r requirements.txt
   ```

For detailed setup instructions, see the [Build Guide](./docs/BUILD.md).

## 🔧 Usage

### Configuration Analysis (config-tool)

Analyze configuration patterns across multiple EOS devices:

```bash
./config-tool.py --directory /path/to/configs \
                 --mask description \
                 --count all
```

Options:
- `--directory PATH`: Location of EOS configuration files
- `--mask STRING`: Ignore specific elements during comparison (e.g., descriptions)
- `--count #|all`: Threshold for considering a stanza "common"
  - Number: Minimum occurrences required
  - `all`: Must appear in every config file

### Configuration Collection (confgrabber)

Pull configurations from live EOS devices:

```bash
./confgrabber.py --user admin \
                 --passwd 'secret' \
                 --file switches \
                 --directory ./configs/
```

Options:
- `--user STRING`: EOS device username
- `--passwd STRING`: EOS device password
- `--file PATH`: File containing list of switch hostnames/IPs
- `--directory PATH`: Output directory for configurations

## ⚡ Performance Optimization

### Python vs Rust Implementation

Choose based on your needs:

| Feature | Python | Rust |
|---------|--------|------|
| Setup Complexity | Simple | Requires compilation |
| Memory Usage | Higher | Lower |
| Processing Speed | Good | Excellent |
| Parallel Processing | Limited | Full support |
| Best For | Development, small deployments | Production, large scale |

See [RUST_USAGE.md](./RUST_USAGE.md) for Rust-specific features and usage.

## 🔒 Security

- Credentials are never stored in configuration files
- Support for environment variables for sensitive data
- Secure eAPI communication
- Optional read-only mode

## 🛠 Development

### Development Environments

1. **VS Code Devcontainer**:
   - Full IDE integration
   - Pre-configured Python environment
   - Optional Rust toolchain
   - Extension recommendations

2. **DevPod**:
   - More stable container management
   - Better Podman support
   - Faster startup times
   - IDE-agnostic

See [Build Guide](./docs/BUILD.md) for detailed development setup instructions.

## 📚 Documentation

- [Build Guide](./docs/BUILD.md): Detailed setup instructions
- [RUST_USAGE.md](./RUST_USAGE.md): Rust implementation details
- [API Documentation](./docs/API.md): eAPI integration details
- [Contributing Guide](./CONTRIBUTING.md): Development guidelines

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) for details on:
- Code style
- Development process
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Arista Networks for EOS and CloudVision
- The Rust and Python communities
- All contributors to this project
