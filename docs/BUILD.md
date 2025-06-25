# Build Guide

This document explains how to build and set up the config-tool project, including both the Python and Rust components.

## Python Setup

The Python components can be run directly without compilation. Just ensure you have the required dependencies:

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

## Rust Binary Build

The project includes a high-performance Rust implementation of the confgrabber tool. Building it is optional - the Python version will work without it.

### Prerequisites

1. Install the Rust toolchain:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. Add your target architecture (if cross-compiling):
   ```bash
   # For macOS ARM (Apple Silicon)
   rustup target add aarch64-apple-darwin
   
   # For macOS Intel
   rustup target add x86_64-apple-darwin
   
   # For Linux ARM64
   rustup target add aarch64-unknown-linux-gnu
   
   # For Linux x86_64
   rustup target add x86_64-unknown-linux-gnu
   ```

### Building

1. **Native Build** (for your current system):
   ```bash
   cargo build --release
   ```
   The binary will be at `target/release/confgrabber`

2. **Cross-Compilation** (for other architectures):
   ```bash
   # For macOS ARM (Apple Silicon)
   cargo build --release --target aarch64-apple-darwin
   
   # For macOS Intel
   cargo build --release --target x86_64-apple-darwin
   
   # For Linux ARM64
   cargo build --release --target aarch64-unknown-linux-gnu
   
   # For Linux x86_64
   cargo build --release --target x86_64-unknown-linux-gnu
   ```
   The binary will be at `target/<target-triple>/release/confgrabber`

### Installation

After building, you can install the binary to your system:

```bash
# Copy to a location in your PATH
sudo cp target/release/confgrabber /usr/local/bin/
```

Or keep it in the project directory and run it locally:

```bash
./target/release/confgrabber --help
```

### Development Build

If you're developing the Rust implementation, you might want to install some helpful tools:

```bash
# Install cargo-watch for auto-rebuilding during development
cargo install cargo-watch

# Install cargo-edit for easier dependency management
cargo install cargo-edit
```

## Using the Development Container

The project includes a devcontainer configuration for VS Code/Cursor that sets up a complete development environment. To use it:

1. Install VS Code or Cursor
2. Install the "Dev Containers" extension
3. Open the project in VS Code/Cursor
4. Click "Reopen in Container" when prompted

The container includes all necessary Python dependencies but does not include the Rust toolchain by default. If you need to work on the Rust implementation, follow the Rust setup steps above inside the container.

## Performance Considerations

- The Python implementation is suitable for most use cases
- The Rust implementation offers better performance for large-scale operations, particularly when:
  - Processing many devices in parallel
  - Handling large configuration files
  - Running on resource-constrained systems

Choose the appropriate implementation based on your needs. 
