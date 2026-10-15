#!/bin/sh

ipq5322_cca_threshold()
{
	local cca_en=$(uci -q get tripleband.tripleband.cca_mitigation || echo "1")
	case "$1" in
		radio0|wifi0)
			wifitool ath0 setUnitTestCmd 67 3 16 0 "$cca_en" 2>/dev/null || true
			;;
		radio1|wifi1)
			wifitool ath1 setUnitTestCmd 67 3 16 1 "$cca_en" 2>/dev/null || true
			;;
	esac
}
