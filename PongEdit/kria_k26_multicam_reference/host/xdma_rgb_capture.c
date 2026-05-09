#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

static void usage(const char *argv0) {
    fprintf(stderr,
            "Usage: %s [options]\n"
            "\n"
            "Options:\n"
            "  --dev <path>          XDMA C2H device, default /dev/xdma0_c2h_0\n"
            "  --out <path>          Output raw RGB file, default capture.rgb\n"
            "  --frames <n>          Number of frames to capture, default 40\n"
            "  --width <pixels>      Width, default 1920\n"
            "  --height <lines>      Height, default 1536\n"
            "  --channels <n>        Number of interleaved camera frames per cycle, default 4\n",
            argv0);
}

static uint32_t parse_u32(const char *s, const char *name) {
    char *end = NULL;
    errno = 0;
    unsigned long value = strtoul(s, &end, 0);
    if (errno || end == s || *end != '\0' || value > UINT32_MAX) {
        fprintf(stderr, "Invalid %s: %s\n", name, s);
        exit(2);
    }
    return (uint32_t)value;
}

static double elapsed_sec(struct timespec a, struct timespec b) {
    return (double)(b.tv_sec - a.tv_sec) + (double)(b.tv_nsec - a.tv_nsec) / 1000000000.0;
}

static bool read_full(int fd, uint8_t *buf, size_t len) {
    size_t done = 0;
    while (done < len) {
        ssize_t rc = read(fd, buf + done, len - done);
        if (rc < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("read XDMA");
            return false;
        }
        if (rc == 0) {
            fprintf(stderr, "Short read from XDMA device\n");
            return false;
        }
        done += (size_t)rc;
    }
    return true;
}

static bool write_full(int fd, const uint8_t *buf, size_t len) {
    size_t done = 0;
    while (done < len) {
        ssize_t rc = write(fd, buf + done, len - done);
        if (rc < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("write output");
            return false;
        }
        done += (size_t)rc;
    }
    return true;
}

int main(int argc, char **argv) {
    const char *dev_path = "/dev/xdma0_c2h_0";
    const char *out_path = "capture.rgb";
    uint32_t frames = 40;
    uint32_t width = 1920;
    uint32_t height = 1536;
    uint32_t channels = 4;

    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--dev") && i + 1 < argc) {
            dev_path = argv[++i];
        } else if (!strcmp(argv[i], "--out") && i + 1 < argc) {
            out_path = argv[++i];
        } else if (!strcmp(argv[i], "--frames") && i + 1 < argc) {
            frames = parse_u32(argv[++i], "frames");
        } else if (!strcmp(argv[i], "--width") && i + 1 < argc) {
            width = parse_u32(argv[++i], "width");
        } else if (!strcmp(argv[i], "--height") && i + 1 < argc) {
            height = parse_u32(argv[++i], "height");
        } else if (!strcmp(argv[i], "--channels") && i + 1 < argc) {
            channels = parse_u32(argv[++i], "channels");
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if (!frames || !width || !height || !channels) {
        usage(argv[0]);
        return 2;
    }

    const size_t frame_bytes = (size_t)width * (size_t)height * 3u;
    const uint64_t total_frames = (uint64_t)frames * (uint64_t)channels;
    const uint64_t total_bytes = (uint64_t)frame_bytes * total_frames;

    uint8_t *buffer = aligned_alloc(4096, (frame_bytes + 4095u) & ~4095u);
    if (!buffer) {
        perror("aligned_alloc");
        return 1;
    }

    int dev_fd = open(dev_path, O_RDONLY);
    if (dev_fd < 0) {
        perror("open XDMA device");
        free(buffer);
        return 1;
    }

    int out_fd = open(out_path, O_CREAT | O_TRUNC | O_WRONLY, 0644);
    if (out_fd < 0) {
        perror("open output");
        close(dev_fd);
        free(buffer);
        return 1;
    }

    struct timespec t0;
    struct timespec t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (uint64_t i = 0; i < total_frames; ++i) {
        if (!read_full(dev_fd, buffer, frame_bytes)) {
            close(out_fd);
            close(dev_fd);
            free(buffer);
            return 1;
        }
        if (!write_full(out_fd, buffer, frame_bytes)) {
            close(out_fd);
            close(dev_fd);
            free(buffer);
            return 1;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    const double seconds = elapsed_sec(t0, t1);
    const double mbps = seconds > 0.0 ? ((double)total_bytes / seconds) / 1000000.0 : 0.0;

    printf("Captured %" PRIu64 " RGB frames to %s\n", total_frames, out_path);
    printf("Frame size: %zu bytes, total: %" PRIu64 " bytes\n", frame_bytes, total_bytes);
    printf("Elapsed: %.3f s, throughput: %.2f MB/s\n", seconds, mbps);

    close(out_fd);
    close(dev_fd);
    free(buffer);
    return 0;
}

