#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/watchdog.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/utsname.h>
#include <unistd.h>

static void record(const char *text) {
    puts(text);
    int fd = open("/dev/kmsg", O_WRONLY | O_CLOEXEC);
    if (fd >= 0) { dprintf(fd, "<6>T7-DIAG: %s\n", text); close(fd); }
}
static void mount_ram(const char *src, const char *dir, const char *type) {
    mkdir(dir, 0755);
    if (mount(src, dir, type, MS_NOSUID | MS_NODEV, NULL))
        printf("mount %s: errno=%d\n", dir, errno);
}
static void dump(const char *path) {
    char buffer[4096]; ssize_t count;
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return;
    printf("--- %s ---\n", path);
    while ((count = read(fd, buffer, sizeof(buffer))) > 0)
        fwrite(buffer, 1, (size_t)count, stdout);
    close(fd);
}
int main(void) {
    mkdir("/dev", 0755);
    if (mount("devtmpfs", "/dev", "devtmpfs", MS_NOSUID, NULL))
        perror("devtmpfs");
    int console = open("/dev/console", O_RDWR);
    if (console >= 0) {
        dup2(console, 0); dup2(console, 1); dup2(console, 2);
        if (console > 2) close(console);
    }
    setvbuf(stdout, NULL, _IONBF, 0);
    mount_ram("proc", "/proc", "proc");
    mount_ram("sysfs", "/sys", "sysfs");
    mount_ram("tmpfs", "/tmp", "tmpfs");
    struct utsname identity;
    record("INIT_REACHED build=t7-diag-20261002-v1");
    if (!uname(&identity))
        printf("kernel=%s arch=%s build=%s\n", identity.release, identity.machine, identity.version);
    dump("/proc/cmdline"); dump("/proc/mounts"); dump("/proc/iomem");
    dump("/proc/mtd");
    /* Keep the conventional watchdog alive if its driver has probed.
       No raw MMIO access, flash mount, shell, installation or reboot. */
    int watchdog = open("/dev/watchdog", O_WRONLY | O_CLOEXEC);
    if (watchdog >= 0) record("WATCHDOG_OPENED");
    else record("WATCHDOG_UNAVAILABLE");
    record("RAM_ONLY_IDLE");
    for (;;) {
        if (watchdog >= 0 && ioctl(watchdog, WDIOC_KEEPALIVE, 0))
            record("WATCHDOG_KEEPALIVE_FAILED");
        sleep(2);
    }
}
