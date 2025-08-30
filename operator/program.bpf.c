#include <uapi/linux/ptrace.h>

struct event_t {
    u32 pid;
    u64 dst;
    u64 src;
    u64 size;
    u8 kind;
};

BPF_PERF_OUTPUT(events);
BPF_HASH(kernel_count, u32, u64);

int trace_cuda_memcpy_async(struct pt_regs *ctx, void *dst, void *src, size_t size, u8 kind) {
    struct event_t event = {};
    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.dst = (u64)dst;
    event.src = (u64)src;
    event.size = size;
    event.kind = kind;

    events.perf_submit(ctx, &event, sizeof(event));
    return 0;
}

int trace_cuda_launch_kernel(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 zero = 0, *val;
    val = kernel_count.lookup_or_init(&pid, &zero);
    (*val)++;
    return 0;
}
