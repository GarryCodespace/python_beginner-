# Vivado Notes

The Vivado files are a hardware-platform scaffold, not a board-locked bitstream.
They define the reference architecture and leave final carrier-board integration
items explicit.

## Build

```tcl
source /Users/garryyuan/python/PongEdit/kria_k26_multicam_reference/vivado/scripts/create_project.tcl
```

The default part is:

```text
xck26-sfvc784-2LV-c
```

Override it if your installed Vivado device database uses a different K26 grade:

```bash
KRIA_K26_PART=xck26-sfvc784-2LV-i vivado -mode tcl
```

## Manual Completion Items

- Confirm the exact K26 SOM and carrier-board part/board files.
- Complete PL PCIe Gen3 x4 GTH lane, reference clock, and reset constraints.
- Connect AXI VDMA memory ports to PS DDR through the selected HP/HPC ports.
- Assign AXI-Lite addresses for the register block and VDMA control ports.
- Replace TPG instances with MIPI CSI-2 RX Subsystem instances after camera
  lane mapping is confirmed.
- Generate XSA for Vitis/PetaLinux after block-design validation.

## Suggested Frame Buffer Layout

For phase 1, allocate three frame buffers per camera:

```text
frame_bytes = 1920 x 1536 x 3 = 8,847,360 bytes
aligned_frame_bytes = 0x00870000
buffers = 4 cameras x 3 buffers = 12 buffers
minimum_pool = 12 x aligned_frame_bytes = about 102 MiB
```

Use larger alignment if required by the final DMA/cache policy.

