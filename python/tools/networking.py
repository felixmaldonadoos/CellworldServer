import socket
import psutil
import re

def get_iface_ips() -> dict:
    ips = {"eth": None, "wifi": None}
    for name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family != socket.AF_INET:
                continue
            if re.search(r"wi[- ]?fi|wlan|wireless", name, re.I):
                ips["wifi"] = addr.address
            elif re.search(r"ethernet|lan", name, re.I):
                ips["eth"] = addr.address
    return ips

# example
if __name__ == "__main__":
    print(get_iface_ips())
