
# Crow USB auxiliary-line protection — 2026-09-22

The new USB front-end uses U_USB_CC_ESD for CC1/CC2 and U_USB_VBUS_ESD for host VBUS. SLLSEG9C pages3–4 were reopened: DRL pin3=IO1, pin4=GND, pin5=IO2; package pins1/2 are NC. The5.5V working range fits the5V-only USB role. The unused VBUS array channel is explicitly unconnected. No CC pins are shorted together and VBUS remains separate from local power. These are shunt clamps at the connector with a short GND return; the separate low-capacitance data array remains on D+/D-.

The2-channel part is already used by the retained analog source. Reusing it avoids introducing another exact part family for one auxiliary channel. Its component ratings do not establish board-level ESD performance or protection coordination; the VBUS sense network and connector return route still require review. Existing donor adjacency proposals apply to the named analog channels only and confer no USB layout acceptance.
