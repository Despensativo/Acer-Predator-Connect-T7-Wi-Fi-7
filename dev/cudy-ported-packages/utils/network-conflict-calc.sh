#!/bin/sh

awk -f - $* <<EOF
function ipchg(ip) {
	split(ip,a,"\.")
	for(ret=0,i=1;i<=4;i++) {
		ret=or(lshift(ret,8),a[i])
	}
	return ret
}

BEGIN{
	lan_ip=ipchg(ARGV[1])
	lan_netmask=ipchg(ARGV[2])
	wan_ip=ipchg(ARGV[3])
	wan_netmask=ipchg(ARGV[4])
	if(and(lan_ip,lan_netmask) == and(wan_ip,lan_netmask) || and(lan_ip,wan_netmask) == and(wan_ip,wan_netmask)) {
		print "1"
	} else {
		print "0"
	}
}
EOF
