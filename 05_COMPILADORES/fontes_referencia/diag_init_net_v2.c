#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/watchdog.h>
#include <net/if.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mount.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/utsname.h>
#include <unistd.h>
#include "identidade-net-v2.h"

static int channels[2] = {-1, -1};
static const char *interfaces[2] = {"lan", "wan"};
static struct utsname identity;
static char bootid[64] = "unknown";
static uint32_t sequence;
static struct sockaddr_in destination;

static void record(const char *text) {
    puts(text);
    int fd = open("/dev/kmsg", O_WRONLY | O_CLOEXEC);
    if (fd >= 0) { dprintf(fd, "<6>T7-NET: %s\n", text); close(fd); }
}
static void request_name(struct ifreq *request, const char *name) {
    memset(request, 0, sizeof(*request));
    snprintf(request->ifr_name, sizeof(request->ifr_name), "%s", name);
}
static int configure_port(unsigned port) {
    int control = socket(AF_INET, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (control < 0) return -1;
    struct ifreq req;
    request_name(&req, interfaces[port]);
    struct sockaddr_in *ip = (struct sockaddr_in *)&req.ifr_addr;
    ip->sin_family = AF_INET;
    ip->sin_addr.s_addr = htonl(0xa9fe4902U + port); /* 169.254.73.2 / .3 */
    if (ioctl(control, SIOCSIFADDR, &req)) goto fail;
    request_name(&req, interfaces[port]);
    ip = (struct sockaddr_in *)&req.ifr_netmask;
    ip->sin_family = AF_INET;
    ip->sin_addr.s_addr = htonl(0xffff0000U);
    if (ioctl(control, SIOCSIFNETMASK, &req)) goto fail;
    request_name(&req, interfaces[port]);
    if (ioctl(control, SIOCGIFFLAGS, &req)) goto fail;
    req.ifr_flags |= IFF_UP;
    if (ioctl(control, SIOCSIFFLAGS, &req)) goto fail;
    int enabled = 1;
    if (setsockopt(control, SOL_SOCKET, SO_BROADCAST, &enabled, sizeof(enabled))) goto fail;
    if (setsockopt(control, SOL_SOCKET, SO_BINDTODEVICE,
                   interfaces[port], strlen(interfaces[port]) + 1)) goto fail;
    struct sockaddr_in local = {.sin_family = AF_INET, .sin_port = 0};
    local.sin_addr.s_addr = htonl(0xa9fe4902U + port);
    if (bind(control, (struct sockaddr *)&local, sizeof(local))) goto fail;
    return control;
fail:
    close(control);
    return -1;
}
static void emit(const char *phase, const char *body) {
    char packet[1200];
    for (unsigned port = 0; port < 2; ++port) {
        if (channels[port] < 0) continue;
        int length = snprintf(packet, sizeof(packet),
            "T7NET1\t%s\t%s\tt7-net-20261002-v2\t%s\t%s\t%s\t%s\t%u\t%.800s",
            T7_NET_ID, bootid, identity.machine, identity.release,
            interfaces[port], phase, ++sequence, body);
        if (length > 0 && (size_t)length < sizeof(packet))
            (void)sendto(channels[port], packet, (size_t)length, MSG_DONTWAIT,
                         (struct sockaddr *)&destination, sizeof(destination));
    }
}
static void mount_ram(const char *src, const char *dir, const char *type) {
    mkdir(dir, 0755);
    if (mount(src, dir, type, MS_NOSUID | MS_NODEV, NULL))
        printf("mount %s errno=%d\n", dir, errno);
}
int main(void) {
    mkdir("/dev", 0755);
    if (mount("devtmpfs", "/dev", "devtmpfs", MS_NOSUID, NULL)) perror("devtmpfs");
    int console = open("/dev/console", O_RDWR);
    if (console >= 0) {
        dup2(console, 0); dup2(console, 1); dup2(console, 2);
        if (console > 2) close(console);
    }
    setvbuf(stdout, NULL, _IONBF, 0);
    mount_ram("proc", "/proc", "proc");
    mount_ram("sysfs", "/sys", "sysfs");
    mount_ram("tmpfs", "/tmp", "tmpfs");
    if (uname(&identity)) memset(&identity, 0, sizeof(identity));
    int fd = open("/proc/sys/kernel/random/boot_id", O_RDONLY | O_CLOEXEC);
    if (fd >= 0) {
        ssize_t length = read(fd, bootid, sizeof(bootid)-1);
        if (length > 0) { bootid[length] = 0; bootid[strcspn(bootid, "\n")] = 0; }
        close(fd);
    }
    record("INIT_REACHED build=t7-net-20261002-v2");
    int watchdog = open("/dev/watchdog", O_WRONLY | O_CLOEXEC);
    int logs = open("/dev/kmsg", O_RDONLY | O_NONBLOCK | O_CLOEXEC);
    destination.sin_family = AF_INET;
    destination.sin_port = htons(6666);
    inet_pton(AF_INET, "169.254.255.255", &destination.sin_addr);
    int have_network = 0;
    for (;;) {
        if (watchdog >= 0) (void)ioctl(watchdog, WDIOC_KEEPALIVE, 0);
        for (unsigned port = 0; port < 2; ++port)
            if (channels[port] < 0) channels[port] = configure_port(port);
        int ready = channels[0] >= 0 || channels[1] >= 0;
        if (ready && !have_network) {
            emit("INIT_REACHED", "Diagnostic init active; RAM-only; no installer");
            have_network = 1;
        }
        if (ready) {
            /* Repeat identity because UDP may be lost during link negotiation. */
            emit("INIT_REACHED", "Diagnostic init active; RAM-only; no installer");
            if (logs >= 0) for (unsigned line = 0; line < 32; ++line) {
                char text[1024];
                ssize_t length = read(logs, text, sizeof(text)-1);
                if (length < 0 && errno == EPIPE) continue;
                if (length <= 0) break;
                text[length] = 0;
                emit("KMSG", text);
            }
            emit("HEARTBEAT", "Alive; flash and modules disabled");
        }
        sleep(2);
    }
}
