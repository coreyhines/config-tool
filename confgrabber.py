#!/usr/bin/env python3

from jsonrpclib import Server
import ssl
import argparse
import os
import multiprocessing
import numpy as np


def grab_config(hostnames, user, passwd, directory, sanitized):
    """download configuration from EOS device using jsonrpc

    Args:
        hostnames (list): list of hostnames
        user (string): user name
        passwd (string): password
        directory (string): directory name
    """
    for hostname in hostnames:
        host = hostname.strip()
        _create_unverified_https_context = ssl._create_unverified_context
        ssl._create_default_https_context = _create_unverified_https_context
        response = os.system(f"ping -c 2 {host} > /dev/null 2>&1")
        if response == 0:
            pingstatus = f"{host}: Network Active"
            print(pingstatus)
            try:
                device = Server(
                    "https://{}:{}@{}/command-api".format(user, passwd, host)
                )
                if sanitized != True:
                    result = device.runCmds(
                        version=1,
                        cmds=["enable", "show running-config"],
                        format="text",
                    )
                else:
                    result = device.runCmds(
                        version=1,
                        cmds=["enable", "show running-config sanitized"],
                        format="text",
                    )
                with open(
                    directory + "/" + host + ".txt",
                    mode="wt",
                    encoding="utf-8",
                ) as writer:
                    for lines in result[1]["output"]:
                        writer.write(lines)
            except Exception as e:
                print(
                    f"something went wrong on {host}, check password\n\n{str(e)}\n"
                )
        else:
            pingstatus = "Network Error"
            print(
                f"{pingstatus}: {host} does not respond to ping, moving on..\n"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--user",
        type=str,
        default="",
        help="specify a username",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--passwd",
        type=str,
        default="",
        help="for passing password interactively",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="",
        help="specify a file with EOS Devices from which to pull the running-config",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=".",
        help="specify a directory to download configs to (note: no trailing '/'",
        required=False,
    )
    parser.add_argument(
        "-s",
        "--sanitized",
        # type=str,
        action="store_true",
        # default="False",
        help="flag for running-config to be sanitized: show running-config sanitized",
        required=False,
    )
    args = parser.parse_args()

    file = args.file
    user = args.user
    passwd = args.passwd
    directory = args.directory
    if args.sanitized:
        sanitized = True
    else:
        sanitized = False

    with open(file, "r") as current_file:
        hostnames = current_file.readlines()
        current_file.close()

    # split the hostnames list array in N parts
    # create a thread for each list
    # run grabconfig() in each thread on subarray of eos devices
    # execute threads
    split = np.array_split(hostnames, 8)
    arr1 = list(split[0])
    arr2 = list(split[1])
    arr3 = list(split[2])
    arr4 = list(split[3])
    arr5 = list(split[4])
    arr6 = list(split[5])
    arr7 = list(split[6])
    arr8 = list(split[7])
    t1 = multiprocessing.Process(
        target=grab_config, args=(arr1, user, passwd, directory, sanitized)
    )
    t2 = multiprocessing.Process(
        target=grab_config, args=(arr2, user, passwd, directory, sanitized)
    )
    t3 = multiprocessing.Process(
        target=grab_config, args=(arr3, user, passwd, directory, sanitized)
    )
    t4 = multiprocessing.Process(
        target=grab_config, args=(arr4, user, passwd, directory, sanitized)
    )
    t5 = multiprocessing.Process(
        target=grab_config, args=(arr5, user, passwd, directory, sanitized)
    )
    t6 = multiprocessing.Process(
        target=grab_config, args=(arr6, user, passwd, directory, sanitized)
    )
    t7 = multiprocessing.Process(
        target=grab_config, args=(arr7, user, passwd, directory, sanitized)
    )
    t8 = multiprocessing.Process(
        target=grab_config, args=(arr8, user, passwd, directory, sanitized)
    )
    # start threads in parallel
    # start_time = time.time()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()
    # end_time = time.time() - start_time
    # join will wait for functions to finish
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
    t8.join()
    print(f"Done!")
    # print(
    #    f"Processing {len(hostnames)} EOS devices took {end_time} time using multiprocessing")


if __name__ == "__main__":
    main()
