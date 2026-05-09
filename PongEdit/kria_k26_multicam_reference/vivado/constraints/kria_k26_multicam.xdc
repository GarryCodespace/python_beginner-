# Carrier-board-specific constraints go here.
#
# This file is intentionally conservative. K26 MIPI, PCIe, clock, and reset
# constraints depend on the selected carrier board and connector routing.
#
# Integration checklist:
# - Map PL GTH lanes used by PCIe Gen3 x4 to the host connector.
# - Add PCIe reference clock and reset constraints.
# - Map MIPI CSI-2 D-PHY lanes or external bridge signals for each camera.
# - Add camera reference clocks and I2C pins.
# - Add LiDAR Ethernet constraints only if a PL Ethernet option is selected.
# - Keep PS Ethernet unconstrained here; it is handled by PS configuration.

