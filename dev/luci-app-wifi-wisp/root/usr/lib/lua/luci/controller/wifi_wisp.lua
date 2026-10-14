-- Licensed to the public under the Apache License 2.0.

module("luci.controller.wifi_wisp", package.seeall)

function index()
	entry({"admin", "network", "wifi_wisp"}, view("wifi_wisp"), _("Wi-Fi WAN / WISP"), 25).dependent = true
end
