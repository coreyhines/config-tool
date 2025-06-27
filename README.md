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
