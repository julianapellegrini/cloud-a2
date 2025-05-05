import subprocess as sp # we will use it to run commands
import re # we will use it to analyse the output and search for what we want
import datetime # we will use it to get the time of the ping and report
import os # we will use it to check if the log file already exists and store a backup if it does


# List of IP addresses to ping
ip_lst = ['127.0.0.1', '8.8.8.8', '124.33.24.6', 'google.com', 'nonexistent.domain']

print("Welcome to our ping tool!")
print("This tool will ping a list of IP addresses and log the results.")
print("Default list of IP addresses: 127.0.0.1', '8.8.8.8', '124.33.24.6', 'google.com', 'nonexistent.domain")
print("Would you like to use our default list of IP addresses? (y/n)")

inp = input("Enter your choice: ").strip().lower()
while inp not in ['y', 'n']:
    inp = input("Enter a valid choice (y/n): ").strip().lower()
if inp == 'y':
    # use the default list of IP addresses
    print("Using default list of IP addresses.")
    ip_lst = ['127.0.0.1', '8.8.8.8', '124.33.24.6', 'google.com', 'nonexistent.domain']
elif inp == 'n':
    ip_lst = []
    print("Please enter the IP addresses you want to ping, one by one.")
    print("Type 'done' when you are finished.")
    while True:
        ip = input("Enter IP address: ").strip()
        # check if the user typed 'done' to finish
        if ip.lower() == 'done':
            break
        # check if the input is valid with regex
        if not (re.match(r'^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$', ip) or # IPv4
                re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', ip)): # domain name
            print("Invalid address format. Please try again.")
            continue
        ip_lst.append(ip)

# now that we have the list of IP addresses, we will ping each one

def pinger(ip_address):
    # result dictionary with default values to store the key results

    result = {
        'ip': ip_address,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': None,
        'error_type': 'N/A',
        'avg_time': 'N/A',
        'packet_loss': 'N/A',
        'ttl': 'N/A',
    }

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
            result['error_type'] = "Timeout"
            result['osi_layer'] = "Layer 3 (Network)"
            result['solution'] = ("This error means there was no connection to the end host in the expected time."
                                  "You could 1. Check the network connection 2. Check the firewall settings "
                                  "3. traceroute the path to the host 4. Check if the host is up. \n")

        elif "Destination host unreachable" in e.stdout:
            result['error_type'] = "Network routing failure"
            result['osi_layer'] = "Layer 3 (Network)"
            result['solution'] = "1. Check subnet mask/gateway\n2. Run 'ipconfig /flushdns'"

        elif "Ping request could not find host" in e.stdout:
            result['error_type'] = "DNS resolution failed"
            result['osi_layer'] = "Layer 7 (Application)"
            result['solution'] = "Check DNS server settings"

        else:
            result['error_type'] = f"Unknown error (Code: {e.returncode})"
            result['osi_layer'] = "N/A"
            result['solution'] = "Check command syntax and permissions"

    except ValueError as ve:
        result['status'] = 'Invalid'
        result['error_type'] = f"Invalid IP format: {str(ve)}"
        result['osi_layer'] = "Layer 7 (Application)"
        result['solution'] = "Verify IP/hostname follows standards\n(Example: 192.168.1.1 or google.com)"

    except Exception as e:
        result['status'] = 'Error'
        result['error_type'] = f"System error: {str(e)}"
        result['osi_layer'] = "N/A"
        result['solution'] = "1. Check Python environment\n2. Verify command permissions"

    return result

# function to write the results to a log file
def write_log(results_list):

    # check if log file already exists and create backup if it does
    if os.path.exists('ping_log.txt'):
        backup_name = f"ping_log_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        os.rename('ping_log.txt', backup_name)

    # write a log file with the information of the ping organized
    with open('ping_log.txt', 'w') as f:
        f.write("Ping Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Created: {datetime.datetime.now()}\n\n")
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
                f.write(f"Suggested Solution: {res['solution']}\n")
                f.write(f"OSI Layer Related to the Error: {res['osi_layer']}\n")

            f.write("-" * 40 + "\n")


# now once the file is run we will ping each IP address and write the results to a log file
# main function to run the script
if __name__ == "__main__":
    print("Let's start pinging!\n")

    # list to store the results of each ping
    results = []

    # ping each IP address in the list
    for ip in ip_lst:
        print(f"Pinging {ip}...")
        ip_result = pinger(ip)
        results.append(ip_result)

        # print summary for the current result so the user can keep track of the process
        print(f"\nPinged: {ip_result['ip']}")
        print(f"Status: {ip_result['status']}")
        if ip_result['status'] == 'Reachable':
            print(f"Latency: {ip_result['avg_time']}")
            print(f"Packet Loss: {ip_result['packet_loss']}")
            print(f"TTL: {ip_result['ttl']}")
        else:
            print(f"Error: {ip_result['error_type']}")

    # write the results to a log file
    write_log(results)

    # print a summary of each result to the console
    print("\nPing Output Summary:")
    print("=" * 60)
    print(f"{'Target':} {'Status':} {'Latency':} {'TTL':}")
    for r in results:
        print(f"{r['ip']:} {r['status']:} {r['avg_time']:} {r['ttl']:}")

    print("\nReport saved to ping_log.txt")
    print("=" * 60)
    print("Thank you for using our ping tool!")
