#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Checking reference design files under: $ROOT"

required=(
  "$ROOT/README.md"
  "$ROOT/docs/architecture.md"
  "$ROOT/docs/bandwidth.md"
  "$ROOT/docs/review_packet.md"
  "$ROOT/vivado/scripts/create_project.tcl"
  "$ROOT/vivado/scripts/create_bd.tcl"
  "$ROOT/vivado/rtl/axis_frame_decimator.v"
  "$ROOT/vivado/rtl/mcvr_registers.v"
  "$ROOT/vitis/linux_control/kria_multicam_ctl.c"
  "$ROOT/host/xdma_rgb_capture.c"
)

for f in "${required[@]}"; do
  test -f "$f"
  echo "ok: ${f#$ROOT/}"
done

echo "Building host utility"
make -C "$ROOT/host" clean all

echo "Building target control utility with host compiler"
make -C "$ROOT/vitis/linux_control" clean all

echo "Done"

