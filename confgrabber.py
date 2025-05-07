#!/usr/bin/env python3

from jsonrpclib import Server
import ssl
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import ping3
from typing import List, Tuple
import time
from functools import partial

def check_device_availability(hostname: str, timeout: int = 2) -> Tuple[str, bool]:
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
    except Exception:
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
    _create_unverified_https_context = ssl._create_unverified_context
    ssl._create_default_https_context = _create_unverified_https_context
    
    # Check device availability
    is_available = check_device_availability(hostname)[1]
    if not is_available:
        return hostname, False, "Device does not respond to ping"
    
    # Implement retry logic
    for attempt in range(max_retries):
        try:
            device = Server(f"https://{user}:{passwd}@{hostname}/command-api")
            cmd = "show running-config sanitized" if sanitized else "show running-config"
            result = device.runCmds(
                version=1,
                cmds=["enable", cmd],
                format="text",
            )
            
            # Write config to file
            output_file = os.path.join(directory, f"{hostname}.txt")
            with open(output_file, mode="wt", encoding="utf-8") as writer:
                for line in result[1]["output"]:
                    writer.write(line)
            return hostname, True, ""
            
        except Exception as e:
            if attempt == max_retries - 1:
                return hostname, False, str(e)
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return hostname, False, "Max retries exceeded"

def grab_configs(hostnames: List[str], user: str, passwd: str, 
                directory: str, sanitized: bool, max_workers: int = None) -> None:
    """Download configurations from multiple EOS devices in parallel.
    
    Args:
        hostnames: List of hostnames
        user: Username
        passwd: Password
        directory: Output directory
        sanitized: Whether to get sanitized config
        max_workers: Maximum number of worker threads
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Create a partial function with fixed arguments
    grab_func = partial(grab_single_config, 
                       user=user, 
                       passwd=passwd, 
                       directory=directory, 
                       sanitized=sanitized)
    
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
                    print(f"Successfully downloaded config from {host}")
                else:
                    print(f"Failed to download config from {host}: {error}")
            except Exception as e:
                print(f"Error processing {hostname}: {str(e)}")

def main():
    parser = argparse.ArgumentParser()
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

    # Read hostnames from file
    with open(args.file, "r") as current_file:
        hostnames = current_file.readlines()

    # Start timing
    start_time = time.time()
    
    # Grab configs in parallel
    grab_configs(
        hostnames=hostnames,
        user=args.user,
        passwd=args.passwd,
        directory=args.directory,
        sanitized=args.sanitized,
        max_workers=args.workers
    )
    
    # Calculate and display execution time
    execution_time = time.time() - start_time
    print(f"\nProcessing {len(hostnames)} EOS devices took {execution_time:.2f} seconds")

if __name__ == "__main__":
    main()
