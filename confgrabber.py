#!/usr/bin/env python3

from __future__ import annotations
from typing import List, Tuple, Optional, Any

try:
    from jsonrpclib import Server
    import jsonrpclib.jsonrpc
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except ImportError:
    print(
        "Error: required packages not installed. Please run: pip install jsonrpclib-pelix requests"
    )
    raise SystemExit(1)

import ssl
import socket
import argparse
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from functools import partial

# Disable SSL verification warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class NoVerifyTransport(jsonrpclib.jsonrpc.Transport):
    """Transport that doesn't verify SSL certificates"""

    def single_request(self, host, handler, request_body, verbose=0):
        # Create an SSL context that doesn't verify certificates
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Force HTTPS connection to use our context
        h = self.make_connection(host)
        if hasattr(h, "_context"):
            h._context = context

        return super().single_request(host, handler, request_body, verbose)


class CommandResult:
    """Type hint for command result object"""

    output: str


def check_port_open(
    hostname: str, port: int = 443, timeout: float = 2.0
) -> Tuple[str, bool]:
    """Check if a TCP port is open on the device.

    Args:
        hostname: The hostname to check
        port: The port to check (default: 443 for HTTPS/eAPI)
        timeout: Socket timeout in seconds

    Returns:
        Tuple of (hostname, is_available)
    """
    hostname = hostname.strip()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        # Try to resolve hostname first
        try:
            socket.gethostbyname(hostname)
        except socket.gaierror:
            return hostname, False

        # Try to connect to the port
        result = sock.connect_ex((hostname, port))
        return hostname, result == 0
    except (socket.timeout, ConnectionRefusedError):
        return hostname, False
    finally:
        sock.close()


def grab_single_config(
    hostname: str,
    user: str,
    passwd: str,
    directory: str,
    sanitized: bool,
    skip_check: bool = False,
    max_retries: int = 3,
) -> Tuple[str, bool, str]:
    """Download configuration from a single EOS device using jsonrpc.

    Args:
        hostname: Device hostname
        user: Username
        passwd: Password
        directory: Output directory
        sanitized: Whether to get sanitized config
        skip_check: Whether to skip liveness check
        max_retries: Maximum number of retry attempts

    Returns:
        Tuple of (hostname, success, error_message)
    """
    hostname = hostname.strip()

    # Check if device is reachable
    if not skip_check:
        is_available = check_port_open(hostname)[1]
        if not is_available:
            return hostname, False, "Device is not reachable on port 443 (eAPI)"

    # URL encode the password to handle special characters
    encoded_passwd = urllib.parse.quote(passwd, safe="")

    # Create a Server instance with our custom transport
    device: Any = Server(
        f"https://{user}:{encoded_passwd}@{hostname}/command-api",
        transport=NoVerifyTransport(),
    )

    # Implement retry logic
    for attempt in range(max_retries):
        try:
            cmd = (
                "show running-config sanitized" if sanitized else "show running-config"
            )
            result: List[CommandResult] = device.runCmds(
                version=1,
                cmds=["enable", cmd],
                format="text",
            )

            # Write config to file
            output_file = os.path.join(directory, f"{hostname}.txt")
            try:
                with open(output_file, mode="wt", encoding="utf-8") as writer:
                    writer.write(result[1].output)  # Access output attribute directly
            except IOError as e:
                return hostname, False, f"Failed to write config file: {str(e)}"
            return hostname, True, ""

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                # Don't retry on auth failures
                return hostname, False, f"Authentication failed: {error_msg}"
            elif "Connection refused" in error_msg:
                return (
                    hostname,
                    False,
                    "Connection refused. Please check if eAPI is enabled on the device.",
                )
            elif attempt == max_retries - 1:
                return (
                    hostname,
                    False,
                    f"Failed after {max_retries} attempts: {error_msg}",
                )
            time.sleep(2**attempt)  # Exponential backoff

    return hostname, False, "Max retries exceeded"


def grab_configs(
    hostnames: List[str],
    user: str,
    passwd: str,
    directory: str,
    sanitized: bool,
    skip_check: bool = False,
    max_workers: Optional[int] = None,
) -> None:
    """Download configurations from multiple EOS devices in parallel.

    Args:
        hostnames: List of hostnames
        user: Username
        passwd: Password
        directory: Output directory
        sanitized: Whether to get sanitized config
        skip_check: Whether to skip liveness check
        max_workers: Maximum number of worker threads
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        print(f"Error creating directory {directory}: {str(e)}")
        raise SystemExit(1)

    # Create a partial function with fixed arguments
    grab_func = partial(
        grab_single_config,
        user=user,
        passwd=passwd,
        directory=directory,
        sanitized=sanitized,
        skip_check=skip_check,
    )

    # Track success/failure counts
    success_count = 0
    failure_count = 0

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_host = {executor.submit(grab_func, host): host for host in hostnames}

        # Process results as they complete
        for future in as_completed(future_to_host):
            hostname = future_to_host[future]
            try:
                host, success, error = future.result()
                if success:
                    success_count += 1
                    print(f"✓ Successfully downloaded config from {host}")
                else:
                    failure_count += 1
                    print(f"✗ Failed to download config from {host}: {error}")
            except Exception as e:
                failure_count += 1
                print(f"✗ Error processing {hostname}: {str(e)}")

    # Print summary
    total = len(hostnames)
    print("\nSummary:")
    print(f"Total devices: {total}")
    print(f"Successful: {success_count} ({(success_count/total)*100:.1f}%)")
    print(f"Failed: {failure_count} ({(failure_count/total)*100:.1f}%)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download configurations from EOS devices in parallel using eAPI",
        epilog="Example: %(prog)s -u admin -p mypassword -f devices.txt -d configs/",
    )
    parser.add_argument(
        "-u", "--user", type=str, required=True, help="specify a username"
    )
    parser.add_argument(
        "-p",
        "--passwd",
        type=str,
        required=True,
        help="for passing password interactively",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="specify a file with EOS Devices from which to pull the running-config",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=".",
        help="specify a directory to download configs to (note: no trailing '/')",
    )
    parser.add_argument(
        "-s",
        "--sanitized",
        action="store_true",
        help="flag for running-config to be sanitized: show running-config sanitized",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=None,
        help="maximum number of worker threads (default: number of CPU cores)",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="skip liveness check before attempting to connect",
    )
    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.file):
        print(f"Error: Input file '{args.file}' does not exist")
        raise SystemExit(1)

    # Read hostnames from file
    try:
        with open(args.file, "r") as current_file:
            hostnames = [line.strip() for line in current_file if line.strip()]
    except IOError as e:
        print(f"Error reading input file: {str(e)}")
        raise SystemExit(1)

    if not hostnames:
        print("Error: No valid hostnames found in input file")
        raise SystemExit(1)

    # Start timing
    start_time = time.time()

    try:
        # Grab configs in parallel
        grab_configs(
            hostnames=hostnames,
            user=args.user,
            passwd=args.passwd,
            directory=args.directory,
            sanitized=args.sanitized,
            skip_check=args.skip_check,
            max_workers=args.workers,
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        raise SystemExit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        raise SystemExit(1)

    # Calculate and display execution time
    execution_time = time.time() - start_time
    print(
        f"\nProcessing {len(hostnames)} EOS devices took {execution_time:.2f} seconds"
    )


if __name__ == "__main__":
    main()
