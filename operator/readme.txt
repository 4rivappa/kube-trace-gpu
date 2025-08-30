powered by bcc

    __         __            __                                           
   / /____  __/ /_  ___     / /__________ _________     ____ _____  __  __
  / //_/ / / / __ \/ _ \   / __/ ___/ __ `/ ___/ _ \   / __ `/ __ \/ / / /
 / ,< / /_/ / /_/ /  __/  / /_/ /  / /_/ / /__/  __/  / /_/ / /_/ / /_/ / 
/_/|_|\__,_/_.___/\___/   \__/_/   \__,_/\___/\___/   \__, / .___/\__,_/  
                                                     /____/_/             


BPF code

uprobe: libcudart.so (nvidia cuda runtime library)

    ----
    
    bpf_get_current_pid_tgid (no Params)

        used to get the details of processor id and thread group id
        when processor starts, it has an initial thread (this is the first thread of this new thread group)
        thread group id is same as the processor id, with which this thread group is being created

    ----
    
    trace_cuda_memcpy function (ctx, dst, src, size, kind)

        memory copy between host and device (or device to device) asynchronously
        extracted attributes are pid, dst address, src address, size of the copy and kind of copy
        kind of copy includes host to device, device to host, device to device

    ----

    trace_cuda_launch function
    
        launching a CUDA kernel (a GPU function) on the device
        attributes which can be extracted are pid, tgid, grid and block dimensions, kernel function and other pointers
    
    ----
