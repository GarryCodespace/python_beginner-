# Kria K26 Multi-Camera PCIe Reference Design

This package is a review-ready reference design for a 4-camera AMD Kria K26
vision pipeline:

```text
4x MIPI CSI-2 or test-pattern video sources
-> PL video processing
-> RGB frame buffers in DDR
-> PCIe XDMA C2H
-> Linux host application
```

The initial implementation uses 4x Vivado Test Pattern Generator inputs so the
video buffering, PCIe data movement, software control plane, and host capture
flow can be reviewed before carrier-board MIPI pinout and sensor bring-up are
finalized.

## Deliverables

- [docs/architecture.md](docs/architecture.md): system architecture, block
  diagram, raw path rationale, LiDAR option selection, and design assumptions.
- [docs/bandwidth.md](docs/bandwidth.md): camera, DDR, PCIe, and LiDAR
  bandwidth budget.
- [docs/review_packet.md](docs/review_packet.md): concise customer-facing
  progress packet for the 8 May 2026 review.
- [vivado/scripts/create_project.tcl](vivado/scripts/create_project.tcl):
  Vivado project scaffold.
- [vivado/scripts/create_bd.tcl](vivado/scripts/create_bd.tcl): IP integrator
  block-design scaffold for the 4-channel TPG-to-VDMA-to-XDMA design.
- [vivado/rtl/axis_frame_decimator.v](vivado/rtl/axis_frame_decimator.v):
  synthesizable AXI4-Stream video frame-drop block.
- [vivado/rtl/mcvr_registers.v](vivado/rtl/mcvr_registers.v): simple AXI-Lite
  control/status register block.
- [vitis/linux_control/kria_multicam_ctl.c](vitis/linux_control/kria_multicam_ctl.c):
  target-side Linux control example.
- [host/xdma_rgb_capture.c](host/xdma_rgb_capture.c): host-side XDMA C2H raw RGB
  capture example.

## Expected Development Flow

1. Open Vivado 2024.2 or newer.
2. Source the project script:

   ```tcl
   source /Users/garryyuan/python/PongEdit/kria_k26_multicam_reference/vivado/scripts/create_project.tcl
   ```

3. Review and update the carrier-board constraints in
   `vivado/constraints/kria_k26_multicam.xdc`.
4. Generate the block design, validate, synthesize, implement, and export XSA.
5. Build the Linux target control app:

   ```bash
   cd /Users/garryyuan/python/PongEdit/kria_k26_multicam_reference/vitis/linux_control
   make
   ```

6. Build the host capture app:

   ```bash
   cd /Users/garryyuan/python/PongEdit/kria_k26_multicam_reference/host
   make
   ```

## Important Integration Notes

- The reference path is intentionally TPG-first. Replace each TPG with an AMD
  MIPI CSI-2 RX Subsystem plus sensor I2C configuration after the carrier-board
  MIPI interface is confirmed.
- PCIe Gen3 x4 requires the PL PCIe path through K26 GTH transceivers. Confirm
  the selected K26 carrier routes the GTH lanes to the host connector.
- The XDC file contains placeholders because MIPI lane mapping, PCIe lane
  mapping, clocks, and reset pins are carrier-board specific.
- The XDMA Linux driver is assumed to already be available on the host, as
  stated in the project brief.

