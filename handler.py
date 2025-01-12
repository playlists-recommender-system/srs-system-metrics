from typing import Any

def handler(input: dict, context: object) -> dict[str, Any]:
    #Buffer size
    k = 5

    #Loads/init the buffer
    buffers = context.env.get("buffers")
    if buffers == None:
        buffers = {}
        context.env["buffers"] = buffers
    
    #Process metrics
    bytes_sent = input.get("net_io_counters_eth0-bytes_sent")
    bytes_recv = input.get("net_io_counters_eth0-bytes_recv")
    total_bytes = bytes_sent + bytes_recv
    percentage_network_egress = 0

    if total_bytes > 0:
        percentage_network_egress = bytes_sent/total_bytes

    vm_cached = input.get("virtual_memory-cached")
    vm_buffers = input.get("virtual_memory-buffers")
    vm_total = input.get("virtual_memory-total")
    percentage_memory_cached = 0

    if (vm_total) > 0:
        percentage_memory_cached = (vm_buffers + vm_cached)/vm_total

    data = {
        "percentage_network_egress": percentage_network_egress,
        "percentage_memory_cached": percentage_memory_cached
    }

    """
    #Get rolling mean from cpu percent usage
        #get all cpus in the metrics json
        #for each cpu
            #get the buffer of the cpu from the buffers
            #if that cpu not exists in the buffer)
                #create the buffer for the cpu with k size and the first value in all positions
                #insert the buffer in the buffers variable
                #save the percent as the first value in the main dictionary
            #else(if that cpu exists in the buffer)
                #get the k-1 last positions in the buffer
                #create a new buffer with the new value in the last position
                #update buffer for the cpu
                #compute the mean of the values in the buffer and save in the main dictionary

            #save buffers dictionany in in redis
            #save main dictionary in redis
    """
    cpu_data = {chave:valor for chave, valor in input.items() if "cpu_percent-" in chave}

    for chave, valor in cpu_data.items():
        cpu_buffer = buffers.get(chave)
        if cpu_buffer == None:
            cpu_buffer = [valor for _ in range(1,k)]
            buffers[chave] = cpu_buffer
            data[f"avg-util-cpu{str(chave).replace('cpu_percent-', '')}-60sec"] = valor
        else:
            new_cpu_buffer = cpu_buffer[-k+1:]
            new_cpu_buffer.append(valor)
            buffers[chave] = new_cpu_buffer
            data[f"avg-util-cpu{str(chave).replace('cpu_percent-', '')}-60sec"] = (sum(new_cpu_buffer))/(len(new_cpu_buffer))

    context.env["buffers"] = buffers
    return data
