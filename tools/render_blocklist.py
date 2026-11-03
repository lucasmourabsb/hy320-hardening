#!/usr/bin/env python3
"""Render public IOC facts into owned firewall chains; never contact a device."""
import argparse
import ipaddress
import json
from pathlib import Path
import re

LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")


def normalize_domain(value):
    if not isinstance(value, str) or value != value.strip():
        raise ValueError("Domain must be plain ASCII text without whitespace")
    domain = value.lower()
    labels = domain.split(".")
    if len(domain) > 253 or len(labels) < 2 or not all(LABEL.fullmatch(label) for label in labels):
        raise ValueError("Invalid domain")
    if all(label.isdigit() for label in labels):
        raise ValueError("An IP address is not a domain")
    return domain


def wire_name(domain):
    return b"".join(bytes([len(label)]) + label.encode("ascii") for label in normalize_domain(domain).split(".")) + b"\x00"


def validate(data):
    domains = sorted({normalize_domain(d) for d in data["domains"]})
    if len(domains) != len(data["domains"]):
        raise ValueError("Duplicate normalized domains")
    addresses = []
    for value in data.get("blocked_ipv4", []):
        address = ipaddress.ip_address(value)
        if address.version != 4 or not address.is_global:
            raise ValueError("Only documented public IPv4 indicators are accepted")
        addresses.append(str(address))
    return domains, sorted(set(addresses))


def render_rules(domains, addresses, family):
    if family not in (4, 6):
        raise ValueError("Only IPv4 and IPv6 are supported")
    chain, dns = f"HY320_BB{family}", f"HY320_DNS{family}"
    lines = ["*filter", f":{chain} - [0:0]", f":{dns} - [0:0]", f"-F {chain}", f"-F {dns}"]
    if family == 4:
        lines += [f"-A {chain} -d {ip}/32 -j REJECT" for ip in addresses]
    lines += [f"-A {chain} -p {protocol} --dport 53 -j {dns}" for protocol in ("udp", "tcp")]
    lines.append(f"-A {chain} -j RETURN")
    for domain in domains:
        lines.append(f'-A {dns} -m string --algo kmp --hex-string "|{wire_name(domain).hex()}|" --icase -j REJECT')
    lines += [f"-A {dns} -j RETURN", "COMMIT", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--indicators", type=Path, default=Path(__file__).resolve().parents[1] / "data/indicators.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        domains, addresses = validate(json.loads(args.indicators.read_text()))
    except (ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    args.output.mkdir(parents=True, exist_ok=True)
    for family in (4, 6):
        (args.output / f"badbox-v{family}.rules").write_text(render_rules(domains, addresses, family))
    hosts = "# Merge into the existing hosts file; preserve its original entries.\n"
    hosts += "".join(f"0.0.0.0 {domain}\n:: {domain}\n" for domain in domains)
    (args.output / "hosts.include").write_text(hosts)
    print(json.dumps({"domains": len(domains), "documented_ipv4": len(addresses), "device_contacted": False}))


if __name__ == "__main__":
    main()
