
## Building and Using the Rust Implementation

The Rust implementation provides a fast, parallelized alternative to the Python scripts for grabbing and processing EOS configurations.

### Prerequisites
- [Rust toolchain](https://rustup.rs/) installed (for `cargo` and `rustc`)

### Building
From the project root, run:

```sh
cargo build --release
```

This will produce the binary at `target/release/confgrabber`.

#### Building for Other Architectures (Cross-Compilation)

You can build the Rust binary for different architectures using Cargo's `--target` flag. For example:

- **Build for x86_64 (Intel/AMD 64-bit):**
  ```sh
  cargo build --release --target x86_64-unknown-linux-gnu
  ```

- **Build for ARM64 (Apple Silicon, Raspberry Pi, etc):**
  ```sh
  cargo build --release --target aarch64-apple-darwin
  # or for Linux ARM64:
  cargo build --release --target aarch64-unknown-linux-gnu
  ```

You may need to install the appropriate target first. For example:

```sh
rustup target add x86_64-unknown-linux-gnu
rustup target add aarch64-apple-darwin
rustup target add aarch64-unknown-linux-gnu
```

The resulting binary will be in `target/<target-triple>/release/confgrabber`.

### Usage
The Rust binary replicates the functionality of `confgrabber.py` and can be run as follows:

```sh
./target/release/confgrabber --user <username> --passwd <password> --file <switch_list_file> --directory <output_dir>
```

- `--user <username>`: EOS device username
- `--passwd <password>`: EOS device password
- `--file <switch_list_file>`: File containing a list of switches (one per line)
- `--directory <output_dir>`: Directory to store downloaded configs (default: current directory)
- `--sanitized`: (Optional) Download sanitized running-configs
- `--workers <N>`: (Optional) Limit the number of parallel downloads

#### Example
```sh
./target/release/confgrabber --user admin --passwd 'secret' --file hosts.txt --directory ./configs/
```

### Notes
- The Rust implementation is functionally similar to the Python version but is generally faster for large device lists.
- You can use either the Python or Rust version as needed.
