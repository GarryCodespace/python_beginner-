# Bandwidth Budget

## Camera Payload

Resolution per camera:

```text
1920 x 1536 = 2,949,120 pixels/frame
```

Camera output before conversion, YUV422 8-bit:

```text
2 bytes/pixel
2,949,120 x 2 = 5,898,240 bytes/frame
```

Raw host payload after RGB888 conversion:

```text
3 bytes/pixel
2,949,120 x 3 = 8,847,360 bytes/frame
```

## Per-Camera Rates

At sensor capture rate, 30 fps:

```text
YUV422 input  = 5,898,240 x 30 = 176,947,200 B/s = 168.75 MiB/s
RGB888 output = 8,847,360 x 30 = 265,420,800 B/s = 253.13 MiB/s
```

At host export rate, 10 fps:

```text
RGB888 output = 8,847,360 x 10 = 88,473,600 B/s = 84.38 MiB/s
```

## Four-Camera Rates

If all four cameras are written to DDR as RGB888 at 30 fps before decimation:

```text
4 x 265,420,800 B/s = 1,061,683,200 B/s
about 1.06 GB/s, or 1,012.5 MiB/s
```

If only decimated 10 fps RGB frames are sent to the host:

```text
4 x 88,473,600 B/s = 353,894,400 B/s
about 354 MB/s, or 337.5 MiB/s
```

## PCIe Gen3 x4

PCIe Gen3 uses 8.0 GT/s per lane with 128b/130b encoding. The practical payload
rate depends on payload size, DMA efficiency, host root complex, driver, and
buffer alignment. The project target of approximately 3.2 GB/s is sufficient for
the 354 MB/s 10 fps raw RGB host stream plus LiDAR and sideband metadata.

Recommended first milestone:

- Use large contiguous or scatter-gather host buffers.
- Use frame-aligned transfers.
- Avoid per-line DMA transactions.
- Use polling first, then interrupts after stable transfer is proven.

## DDR Considerations

The highest early bandwidth load is not PCIe; it is DDR traffic if the design
writes all 30 fps RGB frames and reads only selected frames later. A more
efficient option is to decimate before the VDMA writer, so only 10 fps per
camera is committed to the host-facing RGB buffer pool.

Recommended phase-1 choice:

```text
Convert to RGB in PL -> decimate -> write selected RGB frames to DDR
```

This keeps DDR write bandwidth near 354 MB/s for host-facing frames. If a full
30 fps rolling history is required later, add a second circular buffer pool and
budget the extra DDR traffic explicitly.

## LiDAR

Per LiDAR:

```text
100 Mbps = 12.5 MB/s raw line rate before protocol overhead
```

Even four LiDAR inputs are small compared with the video stream:

```text
4 x 12.5 MB/s = 50 MB/s
```

For phase 1, PS Ethernet with Linux UDP is sufficient and simpler. PL Ethernet
can be revisited if deterministic timestamping or direct packet-to-DDR hardware
capture becomes a hard requirement.

