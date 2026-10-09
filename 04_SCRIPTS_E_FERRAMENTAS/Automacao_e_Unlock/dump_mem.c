#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <phys_addr_hex> <size_hex_or_dec>\n", argv[0]);
        return 1;
    }
    uintptr_t phys_addr = strtoul(argv[1], NULL, 0);
    size_t size = strtoul(argv[2], NULL, 0);

    int fd = open("/dev/mem", O_RDONLY | O_SYNC);
    if (fd < 0) {
        perror("open /dev/mem");
        return 1;
    }

    size_t page_size = getpagesize();
    uintptr_t page_base = phys_addr & ~(page_size - 1);
    size_t page_offset = phys_addr - page_base;
    size_t map_size = ((page_offset + size + page_size - 1) / page_size) * page_size;

    void *map = mmap(NULL, map_size, PROT_READ, MAP_SHARED, fd, page_base);
    if (map == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return 1;
    }

    const uint8_t *ptr = (const uint8_t *)map + page_offset;
    size_t written = 0;
    while (written < size) {
        ssize_t n = write(STDOUT_FILENO, ptr + written, size - written);
        if (n <= 0) break;
        written += n;
    }

    munmap(map, map_size);
    close(fd);
    return 0;
}
