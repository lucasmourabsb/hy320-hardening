#!/system/bin/sh
# Finite owner-requested hardening. Keep authenticated network ADB available.
set -eu
umask 077
STATE=/data/misc/hy320-security
mkdir -p "$STATE"
chown 0:0 "$STATE"
chmod 700 "$STATE"

echo 1 > /proc/sys/kernel/dmesg_restrict
echo 1 > /proc/sys/fs/protected_hardlinks
echo 1 > /proc/sys/fs/protected_symlinks
echo 2 > /proc/sys/fs/protected_regular
echo 2 > /proc/sys/fs/protected_fifos

# --noflush only replaces our own chain; Android and BADBOX chains stay intact.
/system/bin/iptables-restore -w 5 --test --noflush < /system/etc/hy320-input-v4.rules
/system/bin/iptables-restore -w 5 --noflush < /system/etc/hy320-input-v4.rules

# Preserve peers on any directly connected global IPv6 LAN prefix present now.
V6="$STATE/input-v6.rules"
cat /system/etc/hy320-input-v6.rules > "$V6"
/system/bin/ip -6 route show table main | /system/bin/awk '
    $1 ~ /^[0-9a-fA-F:]+\/[0-9]+$/ && $2 == "dev" && $3 != "lo" {
        print "-A HY320_IN6 -s " $1 " -j RETURN"
    }' >> "$V6"
echo '-A HY320_IN6 -j DROP' >> "$V6"
echo COMMIT >> "$V6"
/system/bin/ip6tables-restore -w 5 --test --noflush < "$V6"
/system/bin/ip6tables-restore -w 5 --noflush < "$V6"
rm -f "$V6"

/system/bin/iptables -w 5 -C INPUT -j HY320_IN4 2>/dev/null || /system/bin/iptables -w 5 -I INPUT 1 -j HY320_IN4
/system/bin/ip6tables -w 5 -C INPUT -j HY320_IN6 2>/dev/null || /system/bin/ip6tables -w 5 -I INPUT 1 -j HY320_IN6

# Use the authenticated TLS listener without changing the owner's stable IPv4 port.
# Existing sessions survive until the host reconnects; fresh TCP/5555 goes to TLS.
setprop persist.adb.tls_server.enable 1
TLS_READY=0
TRIES=0
while [ "$TRIES" -lt 20 ]; do
    PORT=$(getprop service.adb.tls.port)
    case "$PORT" in
        ''|*[!0-9]*) ;;
        *)
            if [ "$PORT" -gt 0 ] && [ "$PORT" -lt 65536 ]; then
                HEX=$(printf '%04X' "$PORT")
                if awk -v suffix=":$HEX" '$4 == "0A" && substr($2,length($2)-length(suffix)+1) == suffix {found=1} END {exit !found}' /proc/net/tcp /proc/net/tcp6; then
                    TLS_READY=1
                    break
                fi
            fi
            ;;
    esac
    TRIES=$((TRIES + 1))
    sleep 0.25
done
if [ "$TLS_READY" = 1 ]; then
    NAT="$STATE/tls-v4.rules"
    cat > "$NAT" <<EOF
*nat
:HY320_TLS4 - [0:0]
-F HY320_TLS4
-A HY320_TLS4 -p tcp -j REDIRECT --to-ports $PORT
COMMIT
EOF
    iptables-restore -w 5 --test --noflush < "$NAT"
    iptables-restore -w 5 --noflush < "$NAT"
    iptables -w 5 -t nat -C PREROUTING -i wlan0 -p tcp --dport 5555 -j HY320_TLS4 2>/dev/null || iptables -w 5 -t nat -I PREROUTING 1 -i wlan0 -p tcp --dport 5555 -j HY320_TLS4
    # IPv6 NAT is absent on this kernel. Block its legacy port instead.
    iptables -w 5 -I HY320_IN4 3 -p tcp --dport 5555 -j DROP
    ip6tables -w 5 -I HY320_IN6 3 -p tcp --dport 5555 -j DROP
    setprop sys.hy320.adb_transport tls
else
    # Preserve authenticated maintenance if this firmware ever fails to start TLS.
    iptables -w 5 -t nat -D PREROUTING -i wlan0 -p tcp --dport 5555 -j HY320_TLS4 2>/dev/null || true
    setprop sys.hy320.adb_transport authenticated-legacy-fallback
fi
/system/bin/setprop sys.hy320.security_guard ready
