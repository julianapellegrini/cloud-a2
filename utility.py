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

# ===============
# LOG MANAGEMENT FUNCTIONS
# ===============

def write_log(results_list: list[list[str]]) -> str:
    """
    Creating and formatting of log file
    :param results_list: Nested list of results for each ping
    :return: None (log created with date and formating in the 'logs')
    """
    # Generating log file name
    creation_time = datetime.datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss")
    log_file_name = f"ping_log {creation_time}.txt"

    # Writing info to the log file
    with open(log_file_name, 'w') as f:
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
        return log_file_name

# ===============
# MAIN (if utility is running for some reason)
# ===============
if __name__ == "__main__":
    print("Welcome to our ping utility!")
