#!/usr/bin/env python3

from __future__ import annotations
from typing import List, Tuple, Optional, Any
try:
    from jsonrpclib import Server
except ImportError:
    print("Error: jsonrpclib not installed. Please run: pip install jsonrpclib-pelix")
    raise SystemExit(1)
try:
    import ping3  # type: ignore
except ImportError:
    print("Error: ping3 not installed. Please run: pip install ping3")
    raise SystemExit(1)

import ssl
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from functools import partial

class CommandResult:
    """Type hint for command result object"""
    output: str

def check_device_availability(hostname: str, timeout: float = 2.0) -> Tuple[str, bool]:
    """Check if a device is available via ping.
    
    Args:
        hostname: The hostname to check
        timeout: Ping timeout in seconds
        
    Returns:
        Tuple of (hostname, is_available)
    """
    try:
        ping_result = ping3.ping(hostname.strip(), timeout=timeout, unit='ms')
        return hostname.strip(), ping_result is not None
    except Exception as e:
        print(f"Warning: Error pinging {hostname}: {str(e)}")
        return hostname.strip(), False

def grab_single_config(hostname: str, user: str, passwd: str, directory: str, 
                      sanitized: bool, max_retries: int = 3) -> Tuple[str, bool, str]:
    """Download configuration from a single EOS device using jsonrpc.
    
    Args:
        hostname: Device hostname
        user: Username
        passwd: Password
        directory: Output directory
        sanitized: Whether to get sanitized config
        max_retries: Maximum number of retry attempts
        
    Returns:
        Tuple of (hostname, success, error_message)
    """
    hostname = hostname.strip()
    
    try:
        _create_unverified_https_context = ssl._create_unverified_context
        ssl._create_default_https_context = _create_unverified_https_context
    except AttributeError:
        print("Warning: Unable to disable SSL verification. This might cause connection issues.")
    
    # Check device availability
    is_available = check_device_availability(hostname)[1]
    if not is_available:
        return hostname, False, "Device does not respond to ping"
    
    # Implement retry logic
    for attempt in range(max_retries):
        try:
            device: Any = Server(f"https://{user}:{passwd}@{hostname}/command-api")
            cmd = "show running-config sanitized" if sanitized else "show running-config"
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
            if "401 Unauthorized" in error_msg:
                return hostname, False, "Authentication failed. Please check username and password."
            elif "Connection refused" in error_msg:
                return hostname, False, "Connection refused. Please check if eAPI is enabled on the device."
            elif attempt == max_retries - 1:
                return hostname, False, f"Failed after {max_retries} attempts: {error_msg}"
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return hostname, False, "Max retries exceeded"

def grab_configs(hostnames: List[str], user: str, passwd: str, 
                directory: str, sanitized: bool, max_workers: Optional[int] = None) -> None:
    """Download configurations from multiple EOS devices in parallel.
    
    Args:
        hostnames: List of hostnames
        user: Username
        passwd: Password
        directory: Output directory
        sanitized: Whether to get sanitized config
        max_workers: Maximum number of worker threads
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        print(f"Error creating directory {directory}: {str(e)}")
        raise SystemExit(1)
    
    # Create a partial function with fixed arguments
    grab_func = partial(grab_single_config, 
                       user=user, 
                       passwd=passwd, 
                       directory=directory, 
                       sanitized=sanitized)
    
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
    print(f"\nSummary:")
    print(f"Total devices: {total}")
    print(f"Successful: {success_count} ({(success_count/total)*100:.1f}%)")
    print(f"Failed: {failure_count} ({(failure_count/total)*100:.1f}%)")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download configurations from EOS devices in parallel using eAPI",
        epilog="Example: %(prog)s -u admin -p mypassword -f devices.txt -d configs/"
    )
    parser.add_argument("-u", "--user", type=str, required=True,
                      help="specify a username")
    parser.add_argument("-p", "--passwd", type=str, required=True,
                      help="for passing password interactively")
    parser.add_argument("-f", "--file", type=str, required=True,
                      help="specify a file with EOS Devices from which to pull the running-config")
    parser.add_argument("-d", "--directory", type=str, default=".",
                      help="specify a directory to download configs to (note: no trailing '/')")
    parser.add_argument("-s", "--sanitized", action="store_true",
                      help="flag for running-config to be sanitized: show running-config sanitized")
    parser.add_argument("-w", "--workers", type=int, default=None,
                      help="maximum number of worker threads (default: number of CPU cores)")
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
            max_workers=args.workers
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        raise SystemExit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        raise SystemExit(1)
    
    # Calculate and display execution time
    execution_time = time.time() - start_time
    print(f"\nProcessing {len(hostnames)} EOS devices took {execution_time:.2f} seconds")

if __name__ == "__main__":
    main()
