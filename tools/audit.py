#!/usr/bin/env python3
"""Collect allowlisted security facts over an already authorized ADB connection."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import zlib

PROPERTIES = {
    "device_variant": "getprop ro.product.device",
    "android_release": "getprop ro.build.version.release",
    "android_api": "getprop ro.build.version.sdk",
    "security_patch": "getprop ro.build.version.security_patch",
    "build_tags": "getprop ro.build.tags",
    "verified_boot": "getprop ro.boot.verifiedbootstate",
    "verity_mode": "getprop ro.boot.veritymode",
    "selinux_state": "getenforce",
    "adb_enabled": "settings get global adb_enabled",
    "adb_authentication": "getprop ro.adb.secure",
    "adb_transport_guard": "getprop sys.hy320.adb_transport",
    "adb_tls_listener": "getprop service.adb.tls.port",
    "maintenance_uid": "id -u",
    "cpu_governor": "cat /sys/devices/system/cpu/cpufreq/policy0/scaling_governor",
    "cpu_max_khz": "cat /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq",
    "thermal_mode": "cat /sys/class/thermal/thermal_zone0/mode",
    "badbox_guard": "getprop sys.hy320.badbox_guard",
    "security_guard": "getprop sys.hy320.security_guard",
}
ALLOWED_CONFIG = {
    "CONFIG_SECURITY", "CONFIG_SECURITYFS", "CONFIG_SECURITY_SELINUX",
    "CONFIG_SECURITY_APPARMOR", "CONFIG_SECURITY_LANDLOCK", "CONFIG_SECURITY_YAMA",
    "CONFIG_SECURITY_DMESG_RESTRICT", "CONFIG_KEXEC",
}


def parse_config(text):
    result = {}
    for line in text.splitlines():
        if line.startswith("# CONFIG_") and line.endswith(" is not set"):
            key, value = line[2:-11], "n"
        elif "=" in line:
            key, value = line.split("=", 1)
        else:
            continue
        if key in ALLOWED_CONFIG and value in ("y", "m", "n"):
            result[key] = value
    return result


def safe_scalar(name, value):
    value = value.strip()
    # Reject unexpected multi-line output, addresses, keys and error strings.
    if not value or len(value) > 100 or not re.fullmatch(r"[A-Za-z0-9_.,+\-]+", value):
        return None
    if re.search(r"(?:\d{1,3}\.){3}\d{1,3}", value) or "@" in value:
        return None
    if name == "adb_transport_guard" and value not in ("tls", "authenticated-legacy-fallback"):
        return None
    return value


def collect(run):
    """run takes an argv suffix, returning (exit_code, stdout_bytes)."""
    report = {"read_only": True, "properties": {}, "kernel_security_config": {}}
    for name, command in PROPERTIES.items():
        code, output = run(["shell", command])
        report["properties"][name] = safe_scalar(name, output.decode("utf-8", "replace")) if code == 0 else None
    code, data = run(["exec-out", "head", "-c", "524288", "/proc/config.gz"])
    if code == 0 and data:
        try:
            decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
            config = decoder.decompress(data, 2_000_000)
            if decoder.eof:
                report["kernel_security_config"] = parse_config(config.decode("utf-8", "replace"))
        except zlib.error:
            pass
    options = report["kernel_security_config"]
    report["selinux_compiled_in"] = {"y": True, "n": False}.get(options.get("CONFIG_SECURITY_SELINUX"))
    report["matches_documented_variant"] = report["properties"]["device_variant"] == "t950s_be311"
    report["assessment"] = "Exposure reduction only; this audit does not establish trusted firmware or malware absence."
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True, help="An already authorized ADB device selector; omitted from the report")
    parser.add_argument("--adb", default="adb", help="Path to official platform-tools adb")
    parser.add_argument("--server-port", type=int, default=5037)
    parser.add_argument("--output", type=Path, help="Optional private report path; do not commit device reports")
    args = parser.parse_args()
    if not 1 <= args.server_port <= 65535:
        parser.error("Invalid ADB server port")
    base = [args.adb, "-P", str(args.server_port), "-s", args.serial]

    def run(suffix):
        try:
            result = subprocess.run(base + suffix, capture_output=True, timeout=15)
            return result.returncode, result.stdout
        except subprocess.TimeoutExpired:
            return 1, b""

    code, _ = run(["get-state"])
    if code != 0:
        parser.exit(2, "The selected device is unavailable. Establish an authorized ADB connection first.\n")
    report = collect(run)
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # Open the final component without following an existing symbolic link.
        import os
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(args.output, flags, 0o600)
        with os.fdopen(descriptor, "w") as destination:
            os.fchmod(destination.fileno(), 0o600)
            destination.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
