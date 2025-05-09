import ipaddress  # for ip validation
import socket  # for dns validation and resolution
import subprocess as sp  # we will use it to run commands
import re  # we will use it to analyse the output and search for what we want
import datetime  # we will use it to get the time of the ping and report
from copy import copy

# ========================
# FIXTURES
# ========================

# Default addresses to check connectivity with
default_set_of_addresses = ['127.0.0.1', '8.8.8.8', '124.33.24.6', 'google.com', 'nonexistent.domain']

# Pinging result template
ping_result_template = {
    'ip': None,
    'timestamp': None,
    'status': None,
    'error_type': 'N/A',
    'avg_time': 'N/A',
    'packet_loss': 'N/A',
    'ttl': 'N/A',
}

# ========================
# UTILITY FUNCTIONS
# ========================

def is_valid_ip(ip: str) -> bool:
    """
    Function to check if an IP address is a valid IPv4 or IPv6 address.
    :param ip: input IPv4 or IPv6 address
    :return: True or False depending on if the IP address is valid
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def version_of_ip(ip: str) -> str:
    """
    Function that returns the version number of the IP address.
    :param ip: input IPv4 or IPv6 address
    :return: IP version number (4 or 6)
    """
    return str(ipaddress.ip_address(ip).version)

def resolve_name(name):
    """
    Resolve DNS name to IP address.
    :param name: input DNS name
    :return: ipv4 address of the host
    """
    try:
        ip = socket.gethostbyname(name)
        return ip
    except socket.gaierror:
        return None

def pinger(ip_address: str) -> dict[str, str]:
    """
    Function to ping an address.
    :param ip_address:
    :return: result of the ping command
    """
    # result dictionary with default values to store the key results
    result = copy(ping_result_template)
    result['ip'] = ip_address
    result["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # command to ping the IP address
        # captures the output and returns it as a string
        # timeout is set to 10 seconds to avoid hanging the script if the host is unreachable
        # check=True will raise an exception if the command fails, and we will handle it later
        p = sp.run('ping ' + ip_address, capture_output=True, text=True, check=True)

        result['status'] = 'Reachable'
        # if the ping was successful, we will extract the key parts of the output
        # it is stored in the output of the command on the stdout
        # we will use re search to find each one
        time_match = re.search(r'Average = (\d+)ms', p.stdout)
        loss_match = re.search(r'Lost = \d+ \((\d+)% loss\)', p.stdout)
        ttl_match = re.search(r'TTL=(\d+)', p.stdout)

        # group(1) will return the first group of the regex match
        # if the regex did not match, the value will be set to 'N/A'
        result['avg_time'] = f"{time_match.group(1)}ms" if time_match else 'N/A'
        result['packet_loss'] = f"{loss_match.group(1)}%" if loss_match else 'N/A'
        result['ttl'] = ttl_match.group(1) if ttl_match else 'N/A'

    # CalledProcessError will be raised if the return code of the command is not 0
    # this means that the ping was not successful
    except sp.CalledProcessError as e:
        result['status'] = 'Unreachable'
        # determine failure reason, relate to OSI, and suggest solutions
        if "Request timed out" in e.stdout:
            result['error_type'] = "Request timed out"

        elif "Destination host unreachable" in e.stdout:
            result['error_type'] = "Destination host unreachable"

        elif "Ping request could not find host" in e.stdout:
            result['error_type'] = "Ping request could not find host"

        else:
            result['error_type'] = f"Unknown error (Code: {e.returncode})"

    except ValueError as ve:
        result['status'] = 'Invalid'
        result['error_type'] = f"Invalid IP format: {str(ve)}"

    except Exception as e:
        result['status'] = 'Error'
        result['error_type'] = f"System error: {str(e)}"

    return result

# ========================
# USER INTERFACE FUNCTIONS
# ========================

def validate_list_of_ips(ips: list[str]) -> list[bool]:
    """
    Function to check validity of a list of IP addresses.
    :param ips: input list of IP addresses
    :return: list of boolean indicating if the IP addresses are valid
    """
    return [is_valid_ip(ip) for ip in ips]

def request_list_of_addresses() -> list[str]:
    """
    Function to request a list of addresses from the user.
    :return: list of addresses
    """
    amount_of_addresses = int(input("How many IP addresses do you want to check? "))
    addresses = []
    address_num = 1
    while address_num <= amount_of_addresses:
        current_address = input(f"Enter IP address #{address_num}:\t")
        # Checking if address is valid
        if is_valid_ip(resolve_name(current_address)):
            addresses.append(current_address)
            address_num += 1
        else:
            print("Invalid IP address; Try again.")
            continue
    # Introspect the list for user
    print("\n Your list of IP addresses is:")
    for num, address in enumerate(addresses):
        print(num + 1, ":\t", address)
    return addresses

def yes_or_no_students() -> bool | None:
    """
    Function to ask if a user confirmed yes or no. Works slow without Maestro
    :return: True for Yes, False for No
    """
    while True:
        answer = input("Please answer with yes or no (y/n):\t")
        if answer.lower() in ['y', 'yes']:
            return True
            break
        elif answer.lower() in ['n', 'no']:
            return False
            break
        else:
            print("Invalid answer. Try again.")
            continue
    return None

# ===============
# LOG MANAGEMENT FUNCTIONS
# ===============

def write_log(results_list: list[list[str]]) -> str:
    """
    Creating and formatting of log file
    :param results_list: Nested list of results for each ping
    :return: None (log created with date and formating in the 'logs' folder)
    """
    # Generating log file name
    creation_time = datetime.datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss")
    log_file_name = f"ping_log_backup_{creation_time}.txt"

    # Writing info to the log file
    with open('./logs/' + log_file_name, 'w') as f:
        f.write("Ping Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Created: {creation_time}\n\n")
        f.write("-" * 40 + "\n\n")

        for res in results_list:
            f.write(f"Target: {res['ip']}\n")
            f.write(f"Status: {res['status']}\n")
            f.write(f"Timestamp: {res['timestamp']}\n")

            if res['status'] == 'Reachable':
                f.write(f"Average Trip Time: {res['avg_time']}\n")
                f.write(f"Packet Loss Percentage: {res['packet_loss']}\n")
                f.write(f"TTL: {res['ttl']}\n")
            else:
                f.write(f"Error Type: {res['error_type']}\n")

            f.write("-" * 40 + "\n")
        return "logs/" + log_file_name

# ===============
# MAIN (if utility is running for some reason)
# ===============
if __name__ == "__main__":
    print("Welcome to our ping utility!")
