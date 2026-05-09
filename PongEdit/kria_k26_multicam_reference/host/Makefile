CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -std=c11

all: xdma_rgb_capture

xdma_rgb_capture: xdma_rgb_capture.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f xdma_rgb_capture

.PHONY: all clean

