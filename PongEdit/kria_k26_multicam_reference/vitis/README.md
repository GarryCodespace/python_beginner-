# Vitis / Linux Notes

The phase-1 software role on the Kria A53 is control and monitoring:

- program frame dimensions and decimation factor;
- enable/disable the PL stream;
- configure VDMA frame buffer addresses using the Linux driver or `/dev/mem`
  during early bring-up;
- receive LiDAR UDP packets through PS Ethernet;
- expose status to the host or log locally.

The included `linux_control/kria_multicam_ctl.c` utility targets the custom
AXI-Lite register block. It is intentionally small so it can run in early
PetaLinux/rootfs images without extra dependencies.

Build on target or with the selected cross compiler:

```bash
make -C /Users/garryyuan/python/PongEdit/kria_k26_multicam_reference/vitis/linux_control
```

Example on target after Vivado address assignment:

```bash
sudo ./kria_multicam_ctl \
  --base 0xA0000000 \
  --width 1920 \
  --height 1536 \
  --frame-bytes 8847360 \
  --decimation 3 \
  --enable \
  --status
```

