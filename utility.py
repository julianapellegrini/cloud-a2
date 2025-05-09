import ipaddress
import socket

# ========================
# FIXTURES
# ========================

# default addresses to check connectivity with
default_set_of_addresses = ['127.0.0.1', '8.8.8.8', '124.33.24.6', 'google.com', 'nonexistent.domain']


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

    def yes_or_no_students() -> bool:
        """
        Function to ask if a user confirmed yes or no.
        :return: True for Yes, False for No
        """
        while True:
            answer = input("Please answer with yes or no (y/n)")
            if answer in ['y', 'yes']:
                return True
                break
            elif answer in ['n', 'no']:
                return False
                break
            else:
                print("Invalid answer. Try again.")
                continue


if __name__ == "__main__":
    request_list_of_addresses()
    print("Welcome to our ping tool!")
