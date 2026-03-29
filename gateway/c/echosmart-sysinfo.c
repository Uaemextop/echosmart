/*
 * echosmart-sysinfo — Diagnóstico rápido del sistema para el gateway EchoSmart
 *
 * Compila en la Raspberry Pi:
 *   gcc -O2 -o echosmart-sysinfo echosmart-sysinfo.c
 *
 * Uso:
 *   echosmart-sysinfo            # JSON con info del sistema
 *   echosmart-sysinfo --version  # imprime versión
 *   echosmart-sysinfo --check    # devuelve 0 si el sistema está OK, 1 si hay problemas
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/utsname.h>
#include <sys/sysinfo.h>
#include <sys/statvfs.h>
#include <time.h>

#define VERSION "1.0.0"
#define LOW_DISK_THRESHOLD_MB 512
#define LOW_MEM_THRESHOLD_MB  128

/* ── helpers ────────────────────────────────────────────────────────────── */

static double read_cpu_temp(void)
{
    FILE *f = fopen("/sys/class/thermal/thermal_zone0/temp", "r");
    if (!f) return -1.0;
    int raw = 0;
    if (fscanf(f, "%d", &raw) != 1) raw = 0;
    fclose(f);
    return raw / 1000.0;
}

static void read_hostname(char *buf, size_t n)
{
    if (gethostname(buf, n) != 0)
        strncpy(buf, "unknown", n);
}

/* ── sub-commands ───────────────────────────────────────────────────────── */

static void print_version(void)
{
    printf("echosmart-sysinfo %s\n", VERSION);
}

static int print_json(void)
{
    struct utsname uts;
    struct sysinfo si;
    struct statvfs vfs;
    char hostname[256];

    uname(&uts);
    sysinfo(&si);
    statvfs("/", &vfs);
    read_hostname(hostname, sizeof(hostname));

    double cpu_temp     = read_cpu_temp();
    long   uptime_s     = si.uptime;
    long   total_ram_mb = (long)(si.totalram * si.mem_unit) / (1024 * 1024);
    long   free_ram_mb  = (long)(si.freeram  * si.mem_unit) / (1024 * 1024);
    long   total_disk_mb = (long)((unsigned long long)vfs.f_blocks * vfs.f_frsize / (1024 * 1024));
    long   free_disk_mb  = (long)((unsigned long long)vfs.f_bfree  * vfs.f_frsize / (1024 * 1024));

    printf("{\n");
    printf("  \"version\": \"%s\",\n", VERSION);
    printf("  \"hostname\": \"%s\",\n", hostname);
    printf("  \"os\": \"%s %s\",\n", uts.sysname, uts.release);
    printf("  \"arch\": \"%s\",\n", uts.machine);
    printf("  \"uptime_s\": %ld,\n", uptime_s);
    if (cpu_temp >= 0)
        printf("  \"cpu_temp_c\": %.1f,\n", cpu_temp);
    else
        printf("  \"cpu_temp_c\": null,\n");
    printf("  \"ram_total_mb\": %ld,\n", total_ram_mb);
    printf("  \"ram_free_mb\": %ld,\n", free_ram_mb);
    printf("  \"disk_total_mb\": %ld,\n", total_disk_mb);
    printf("  \"disk_free_mb\": %ld\n",  free_disk_mb);
    printf("}\n");

    return 0;
}

static int check_health(void)
{
    struct sysinfo si;
    struct statvfs vfs;
    int ok = 1;

    sysinfo(&si);
    statvfs("/", &vfs);

    long free_ram_mb  = (long)(si.freeram  * si.mem_unit) / (1024 * 1024);
    long free_disk_mb = (long)((unsigned long long)vfs.f_bfree * vfs.f_frsize / (1024 * 1024));
    double cpu_temp   = read_cpu_temp();

    if (free_ram_mb < LOW_MEM_THRESHOLD_MB) {
        fprintf(stderr, "WARN: RAM libre baja: %ld MB (umbral: %d MB)\n",
                free_ram_mb, LOW_MEM_THRESHOLD_MB);
        ok = 0;
    }
    if (free_disk_mb < LOW_DISK_THRESHOLD_MB) {
        fprintf(stderr, "WARN: Disco libre bajo: %ld MB (umbral: %d MB)\n",
                free_disk_mb, LOW_DISK_THRESHOLD_MB);
        ok = 0;
    }
    if (cpu_temp > 80.0) {
        fprintf(stderr, "WARN: Temperatura CPU alta: %.1f °C\n", cpu_temp);
        ok = 0;
    }

    if (ok)
        printf("OK\n");

    return ok ? 0 : 1;
}

/* ── main ───────────────────────────────────────────────────────────────── */

int main(int argc, char *argv[])
{
    if (argc > 1) {
        if (strcmp(argv[1], "--version") == 0 || strcmp(argv[1], "-v") == 0) {
            print_version();
            return 0;
        }
        if (strcmp(argv[1], "--check") == 0 || strcmp(argv[1], "-c") == 0) {
            return check_health();
        }
        if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
            printf("Uso: echosmart-sysinfo [--version|--check|--help]\n");
            printf("  (sin argumentos)  Imprime información del sistema en JSON\n");
            printf("  --check           Verifica la salud del sistema (código 0=OK, 1=problema)\n");
            printf("  --version         Muestra la versión\n");
            return 0;
        }
        fprintf(stderr, "Argumento desconocido: %s\n", argv[1]);
        return 1;
    }

    return print_json();
}
