# 8 May 2026 Review Packet

## Objective

Provide a reference design for AMD Kria K26 SOM demonstrating four camera video
paths, PL processing, DDR buffering, and PCIe XDMA transfer to a host PC. The
initial implementation uses four test pattern inputs to validate the system
architecture before final MIPI CSI-2 camera integration.

## Proposed Architecture

```text
4x MIPI CSI-2 camera inputs
or 4x Vivado test pattern generators for phase 1
-> AXI4-Stream video
-> YUV422 to RGB888 conversion in PL
-> frame decimation from 30 fps to 10 fps
-> AXI VDMA frame buffers in DDR
-> PCIe XDMA C2H over PL PCIe Gen3 x4
-> Linux host application consuming raw RGB frames
```

## Why Keep Raw Video in PL

Raw RGB video should remain in PL because the datapath is high-bandwidth and
deterministic. Moving frames through the ARM A53 cores would introduce
unnecessary memory copies, cache maintenance, scheduling jitter, and CPU load.
The A53 cores are better used for control tasks such as sensor setup, VDMA/XDMA
configuration, health monitoring, and Ethernet/UDP handling.

## LiDAR Selection

Use PS Ethernet with Linux UDP in the first phase. At approximately 100 Mbps per
LiDAR, the data rate is modest compared with the video path. Linux UDP keeps the
reference design simple and debuggable. A PL Ethernet UDP parser can be added in
a later phase if direct hardware timestamping or deterministic packet handling
is required.

## Phase-1 Deliverables

- Architecture document and block diagram.
- Vivado project scaffold for K26.
- Four test-pattern video channels.
- Frame decimation RTL.
- AXI-Lite control/status RTL.
- VDMA/XDMA block-design scaffold.
- Linux target-side control application.
- Linux host-side XDMA RGB capture application.
- Bandwidth analysis and integration checklist.

## Phase-2 Integration Items

- Replace TPG inputs with MIPI CSI-2 RX Subsystem instances.
- Add real camera sensor I2C initialization.
- Finalize carrier-board MIPI and PCIe XDC constraints.
- Add timestamp metadata and optional H.264/H.265 path.
- Validate sustained XDMA throughput on the selected host PC.

