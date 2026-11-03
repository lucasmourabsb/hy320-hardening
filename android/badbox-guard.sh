#!/system/bin/sh
# Owner-requested, finite firewall setup. No downloads and no background loop.
set -eu
/system/bin/iptables-restore -w 5 --noflush < /system/etc/hy320-badbox-v4.rules
/system/bin/ip6tables-restore -w 5 --noflush < /system/etc/hy320-badbox-v6.rules
/system/bin/iptables -w 5 -C OUTPUT -j HY320_BB4 2>/dev/null || /system/bin/iptables -w 5 -I OUTPUT 1 -j HY320_BB4
/system/bin/ip6tables -w 5 -C OUTPUT -j HY320_BB6 2>/dev/null || /system/bin/ip6tables -w 5 -I OUTPUT 1 -j HY320_BB6
/system/bin/setprop persist.sys.jm.url ""
/system/bin/setprop persist.sys.proxy.url ""
/system/bin/setprop sys.hy320.badbox_guard ready
