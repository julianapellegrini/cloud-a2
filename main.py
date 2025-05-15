import utility

# RUNNING CLI
if __name__ == "__main__":

    # Initial prompting
    print("Welcome to our ping tool!")
    print("This tool will ping following list of addresses and log the results.")
    for number, ip in enumerate(utility.default_set_of_addresses):
        print(f"{number + 1} - {ip}")

    # list to store the results of each ping
    results = []

    # ping each address in the list
    print("Let's start pinging!")
    for ip in utility.default_set_of_addresses:
        print(f"\nPinging {ip}...")
        ip_result = utility.pinger(ip)
        results.append(ip_result)

        # print the summary for the current result so the user can keep track of the process
        print(f"\nPinged: {ip_result['ip']}")
        print(f"Status: {ip_result['status']}")
        if ip_result['status'] == 'Reachable':
            print(f"Latency: {ip_result['avg_time']}")
            print(f"Packet Loss: {ip_result['packet_loss']}")
            print(f"TTL: {ip_result['ttl']}")
        else:
            print(f"Error: {ip_result['error_type']}")

    # write the results to a log file
    log_destination = utility.write_log(results)

    # print a summary of each result to the console
    print("\nPing Output Summary:")
    print("=" * 60)
    print(f"{'Target':} {'Status':} {'Latency':} {'TTL':}")
    for r in results:
        print(f"{r['ip']:} {r['status']:} {r['avg_time']:} {r['ttl']:}")
    print(f"\nReport saved to {log_destination}")
    print("=" * 60)

    # goodbye
    print("Thank you for using our ping tool!")
