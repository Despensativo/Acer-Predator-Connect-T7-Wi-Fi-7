#!/bin/sh

ipq5322_cca_threshold()
{
	case "$1" in
		radio0|wifi0)
			wifitool ath0 setUnitTestCmd 67 3 16 0 1 2>/dev/null || true
			;;
		radio1|wifi1)
			wifitool ath1 setUnitTestCmd 67 3 16 1 1 2>/dev/null || true
			;;
	esac
}
