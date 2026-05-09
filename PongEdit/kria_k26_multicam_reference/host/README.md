# Host XDMA Capture

Build:

```bash
make -C /Users/garryyuan/python/PongEdit/kria_k26_multicam_reference/host
```

Example:

```bash
sudo ./xdma_rgb_capture \
  --dev /dev/xdma0_c2h_0 \
  --out four_camera_capture.rgb \
  --frames 100 \
  --width 1920 \
  --height 1536 \
  --channels 4
```

The output file is raw packed RGB888. The default capture order assumes the XDMA
stream presents camera frames in a repeated channel sequence:

```text
cam0 frame0, cam1 frame0, cam2 frame0, cam3 frame0,
cam0 frame1, cam1 frame1, ...
```

If the final XDMA design exposes one C2H device per channel, run one process per
device with `--channels 1`.

