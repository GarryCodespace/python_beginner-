CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -std=c11

all: kria_multicam_ctl

kria_multicam_ctl: kria_multicam_ctl.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f kria_multicam_ctl

.PHONY: all clean

