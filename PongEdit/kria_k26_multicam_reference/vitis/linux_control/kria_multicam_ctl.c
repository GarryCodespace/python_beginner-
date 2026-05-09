#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

enum {
    REG_CONTROL = 0x00,
    REG_DECIMATION = 0x04,
    REG_WIDTH = 0x08,
    REG_HEIGHT = 0x0c,
    REG_FRAME_BYTES = 0x10,
    REG_STATUS = 0x20,
    REG_FRAME_COUNT0 = 0x24,
    REG_FRAME_COUNT1 = 0x28,
    REG_FRAME_COUNT2 = 0x2c,
    REG_FRAME_COUNT3 = 0x30,
};

static void usage(const char *argv0) {
    fprintf(stderr,
            "Usage: %s --base <phys_addr_hex> [options]\n"
            "\n"
            "Options:\n"
            "  --enable                 Enable video output\n"
            "  --disable                Disable video output\n"
            "  --decimation <n>         Set frame decimation factor, 3 = 10 fps from 30 fps\n"
            "  --width <pixels>         Set active width, default 1920\n"
            "  --height <lines>         Set active height, default 1536\n"
            "  --frame-bytes <bytes>    Set frame payload size, default 8847360\n"
            "  --status                 Print status and frame counters\n",
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

static uint64_t parse_u64(const char *s, const char *name) {
    char *end = NULL;
    errno = 0;
    unsigned long long value = strtoull(s, &end, 0);
    if (errno || end == s || *end != '\0') {
        fprintf(stderr, "Invalid %s: %s\n", name, s);
        exit(2);
    }
    return (uint64_t)value;
}

static void wr32(volatile uint32_t *regs, uint32_t off, uint32_t value) {
    regs[off / 4u] = value;
}

static uint32_t rd32(volatile uint32_t *regs, uint32_t off) {
    return regs[off / 4u];
}

int main(int argc, char **argv) {
    uint64_t base = 0;
    bool have_base = false;
    bool set_enable = false;
    bool enable_value = false;
    bool print_status = false;
    uint32_t decimation = 0;
    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t frame_bytes = 0;

    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--base") && i + 1 < argc) {
            base = parse_u64(argv[++i], "base");
            have_base = true;
        } else if (!strcmp(argv[i], "--enable")) {
            set_enable = true;
            enable_value = true;
        } else if (!strcmp(argv[i], "--disable")) {
            set_enable = true;
            enable_value = false;
        } else if (!strcmp(argv[i], "--decimation") && i + 1 < argc) {
            decimation = parse_u32(argv[++i], "decimation");
        } else if (!strcmp(argv[i], "--width") && i + 1 < argc) {
            width = parse_u32(argv[++i], "width");
        } else if (!strcmp(argv[i], "--height") && i + 1 < argc) {
            height = parse_u32(argv[++i], "height");
        } else if (!strcmp(argv[i], "--frame-bytes") && i + 1 < argc) {
            frame_bytes = parse_u32(argv[++i], "frame-bytes");
        } else if (!strcmp(argv[i], "--status")) {
            print_status = true;
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if (!have_base) {
        usage(argv[0]);
        return 2;
    }

    const long page_size = sysconf(_SC_PAGESIZE);
    const uint64_t page_base = base & ~((uint64_t)page_size - 1u);
    const uint64_t page_off = base - page_base;
    const size_t map_size = (size_t)page_off + 0x1000u;

    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd < 0) {
        perror("open /dev/mem");
        return 1;
    }

    void *map = mmap(NULL, map_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, (off_t)page_base);
    if (map == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return 1;
    }

    volatile uint32_t *regs = (volatile uint32_t *)((uint8_t *)map + page_off);

    if (decimation) {
        wr32(regs, REG_DECIMATION, decimation);
    }
    if (width) {
        wr32(regs, REG_WIDTH, width);
    }
    if (height) {
        wr32(regs, REG_HEIGHT, height);
    }
    if (frame_bytes) {
        wr32(regs, REG_FRAME_BYTES, frame_bytes);
    }
    if (set_enable) {
        uint32_t ctl = rd32(regs, REG_CONTROL);
        if (enable_value) {
            ctl |= 1u;
        } else {
            ctl &= ~1u;
        }
        wr32(regs, REG_CONTROL, ctl);
    }

    if (print_status) {
        printf("CONTROL      0x%08" PRIx32 "\n", rd32(regs, REG_CONTROL));
        printf("DECIMATION   %" PRIu32 "\n", rd32(regs, REG_DECIMATION));
        printf("WIDTH        %" PRIu32 "\n", rd32(regs, REG_WIDTH));
        printf("HEIGHT       %" PRIu32 "\n", rd32(regs, REG_HEIGHT));
        printf("FRAME_BYTES  %" PRIu32 "\n", rd32(regs, REG_FRAME_BYTES));
        printf("STATUS       0x%08" PRIx32 "\n", rd32(regs, REG_STATUS));
        printf("FRAME_COUNT0 %" PRIu32 "\n", rd32(regs, REG_FRAME_COUNT0));
        printf("FRAME_COUNT1 %" PRIu32 "\n", rd32(regs, REG_FRAME_COUNT1));
        printf("FRAME_COUNT2 %" PRIu32 "\n", rd32(regs, REG_FRAME_COUNT2));
        printf("FRAME_COUNT3 %" PRIu32 "\n", rd32(regs, REG_FRAME_COUNT3));
    }

    munmap(map, map_size);
    close(fd);
    return 0;
}

