import argparse
import math
import sys
import random

# Constants
PAGE_SIZE = 4096 # 4 KB the standard page size
PTE_ENTRIES_PER_PROCESS = 524288 # 512K entries in the page table

# Setup and Parsing
parser = argparse.ArgumentParser(description='Cache Simulator')

# Set the flags we will accept
parser.add_argument('-s', type=int, help='Cache Size - KB', dest='cache_size')
parser.add_argument('-b', type=int, help='Block Size - bytes', dest='block_size')
parser.add_argument('-a', type=int, help='Associativity', dest='associativity')
parser.add_argument('-r', type=str, help='Replacement Policy', dest='replacement_policy')
parser.add_argument('-p', type=int, help='Physical Memory - MB', dest='physical_memory')
parser.add_argument('-u', type=int, help='Percentage of physical mem used by OS', dest='utilization')
parser.add_argument('-n', type=int, help='Instructions / Time Slice', dest='instructions')
parser.add_argument('-f', type=str, help='Trace File Name', dest='trace_file', action='append')

# Parse the parameters
args = parser.parse_args()

# Error Trapping
try:
    cache_size = args.cache_size
    if cache_size is None or not (8 <= cache_size <= 8192):
        raise ValueError('Cache Size must be between 8 and 8192 KB.')
    
    block_size = args.block_size
    if block_size is None or not (8 <= block_size <= 64) or (block_size & (block_size - 1)) != 0:
        raise ValueError('Block Size must be 8, 16, 32, or 64 bytes.')
        
    associativity = args.associativity
    valid_associativity = {1, 2, 4, 8, 16}
    if associativity is None or associativity not in valid_associativity:
        raise ValueError('Associativity must be 1, 2, 4, 8, or 16.')
        
    replacement_policy = args.replacement_policy
    if replacement_policy is None or replacement_policy.upper() not in {'RR', 'RND'}:
        raise ValueError('Replacement Policy must be RR (Round Robin) or RND (Random).')
    replacement_policy_str = "Round Robin" if replacement_policy.upper() == "RR" else "Random"
    
    physical_memory = args.physical_memory
    if physical_memory is None or not (128 <= physical_memory <= 4096) or (physical_memory & (physical_memory - 1)) != 0:
        raise ValueError('Physical Memory must be a power of 2 between 128 and 4096 MB.')
        
    utilization = args.utilization
    if utilization is None or not (0 <= utilization <= 100):
        raise ValueError('Utilization must be between 0 and 100%.')
        
    instructions = args.instructions
    if instructions is None or not (instructions == -1 or instructions >= 1):
        raise ValueError('Instructions / Time Slice must be -1 or a positive integer.')
        
    trace_files = args.trace_file
    num_trace_files = len(trace_files) if trace_files else 0
    if not (1 <= num_trace_files <= 3):
        raise ValueError(f'Must specify between 1 and 3 Trace Files. You provided {num_trace_files}.')

except ValueError as e:
    print(f'Error: {e}')
    sys.exit(1)

# 1. Cache Calculated Values
total_blocks = int((cache_size * 1024) / block_size)
rows = total_blocks / associativity
rows = int(rows)

# Bit sizes (must be integers)
block_offset = int(math.log2(block_size))
index = int(math.log2(rows))

# Physical Address (PA) Size (bits)
physical_memory_bytes = physical_memory * (2**20) # MB to Bytes
physical_memory_bits = int(math.log2(physical_memory_bytes))

# Tag Size (bits)
tag = physical_memory_bits - index - block_offset
tag = int(tag)

# Overhead Size (Bytes)
overhead_bits = (tag + 1) * total_blocks
overhead = overhead_bits / 8

# Implementation Memory Size
footprint = cache_size * 1024 + overhead

# Readable footprint
readable_footprint = footprint / 1024

cost = readable_footprint * 0.07

# 2. Physical Memory Calculated Values
pages = int(physical_memory_bytes / PAGE_SIZE)

# Pages for System
system_pages = int(math.ceil((utilization / 100) * pages))

# Physical Page Number (PPN) Size (bits)
page_bits = int(math.log2(pages))

# Page Table Entry (PTE) Size: PPN + 1 Valid Bit
pte_bits = page_bits + 1

# Total RAM for Page Table(s)
total_ram = (PTE_ENTRIES_PER_PROCESS * num_trace_files * pte_bits) / 8

# --- MILESTONE 1: OUTPUT ---
print('Cache Simulator - CS 3853 - Team #17') # Use your team number

instructions_str = 'All' if instructions == -1 else str(instructions)

print('\nTrace File(s):')
for file in trace_files:
    print(f'\t{file}')

print('\n***** Cache Input Parameters *****')
print(f"{'Cache Size:':<32}{cache_size} KB")
print(f"{'Block Size:':<32}{block_size} bytes")
print(f"{'Associativity:':<32}{associativity}")
print(f"{'Replacement Policy:':<32}{replacement_policy_str}")
print(f"{'Physical Memory:':<32}{physical_memory} MB")
print(f"{'Percent Memory Used by System:':<32}{utilization}.0%")
print(f"{'Instructions / Time Slice:':<32}{instructions_str}")

print('\n***** Cache Calculated Values *****')
print(f"{'Total # Blocks:':<32}{total_blocks}")
print(f"{'Tag Size:':<32}{tag} bits (based on actual physical memory)")
print(f"{'Index Size:':<32}{index} bits")
print(f"{'Total # Rows:':<32}{rows}")
print(f"{'Overhead Size:':<32}{overhead:.0f} bytes")
print(f"{'Implementation Memory Size:':<32}{readable_footprint:.2f} KB ({footprint:.0f} bytes)")
print(f"{'Cost:':<32}${cost:.2f} @ $0.07 per KB")

print('\n***** Physical Memory Calculated Values *****')
print(f"{'Number of Physical Pages:':<32}{pages}")
print(f"{'Number of Pages for System:':<32}{system_pages}")
print(f"{'Size of Page Table Entry:':<32}{pte_bits} bits (1 valid bit, {page_bits} for PhysPage)")
print(f"{'Total RAM for Page Table(s):':<32}{total_ram:.0f} bytes (512K entries * {num_trace_files} .trc files * {pte_bits} / 8)")

print('\n' + '---' * 20 + '\n')

# MILESTONE 2: VIRTUAL MEMORY SIMULATION LOGIC
pagesAvailable = pages - system_pages # Total pool of pages for ALL user processes

# Shared pool of physical page numbers
# PPNs available range from 'system_pages' up to 'pages - 1'
free_pages = list(range(system_pages, pages))

# Individual page tables for each process
# {VPN: PPN}
process_page_tables = [{} for _ in range(num_trace_files)] 

# Global VM Counters
pageTableHits = 0      # VA was found in the process's page table (PT Hit)
pagesFromFree = 0      # PT Miss and a free page was available
totalPageFaults = 0    # PT Miss and NO free page was available (Requires Swap)


# Simulate the Page Table lookup
def handle_vm_access(address_int, process_id):
    global pageTableHits, pagesFromFree, totalPageFaults, free_pages

    virtualPageTable = process_page_tables[process_id]
    
    # 1. Calculate the Virtual Page Number (VPN)
    vpn = address_int // PAGE_SIZE
    page_offset = address_int % PAGE_SIZE

    # 2. Check for Page Table Hit
    if vpn in virtualPageTable:
        pageTableHits += 1
        ppn = virtualPageTable[vpn]
        return (ppn * PAGE_SIZE) + page_offset # Return Physical Address (PA)
    
    # 3. Page Table Miss (Page Mapping Required)
    else:
        # Check Free Pool
        if free_pages:
            ppn = free_pages.pop(0) # Take a PPN from the front of the free list
            virtualPageTable[vpn] = ppn # Map VA to PA
            pagesFromFree += 1
            return (ppn * PAGE_SIZE) + page_offset # Return new PA
        else:
            # No free pages. Requires a swap (Page Fault)
            totalPageFaults += 1
            
            # --- Later: IMPLEMENT FULL PAGE REPLACEMENT LOGIC HERE FOR MILESTONE 3 ---
            return None 

# Trace File Processing Loop
# This loop reads the trace files and calls the VM access handler for every address.
for count, tracefile in enumerate(trace_files): 
    
    with open(tracefile, "r") as curFile:
        for line in curFile:
            
            # PROCESS INSTRUCTION FETCH ADDRESSES (EIP)
            if line.startswith("EIP"):
                length = int(line[5:7])
                address_int = int(line[10:18], 16)

                # Iterate through all 4-byte chunks of the instruction
                current_addr = address_int
                while current_addr < address_int + length:
                    handle_vm_access(current_addr, count)
                    current_addr += 4 # Move to the next 4-byte chunk
            
            # PROCESS DATA ACCESS ADDRESSES (dstM and srcM)
            elif line.startswith("dstM"):
                
                # Check dstM
                # dstM address is line[6:14], data check is line[15]
                if line[15] != "-":
                    destAddress_str = line[6:14]
                    if destAddress_str != '00000000': 
                        address_int = int(destAddress_str, 16)
                        # All data accesses are 4 bytes.
                        handle_vm_access(address_int, count)
                
                # Check srcM
                # srcM address is line[33:41], data check is line[44]
                if line[44] != "-":
                    sourceAddress_str = line[33:41] 
                    if sourceAddress_str != '00000000': 
                        address_int = int(sourceAddress_str, 16)
                        # All data accesses are 4 bytes.
                        handle_vm_access(address_int, count)
                        
# FINAL VM METRICS CALCULATION

# Virtual Pages Mapped = Total number of times a VA was mapped (PT Hits + Pages from Free)
virtualPagesMapped = pageTableHits + pagesFromFree

# OUTPUT
print('\n***** VIRTUAL MEMORY SIMULATION RESULTS *****')

print(f"{'Physical Pages Used By SYSTEM:':<32}{system_pages}")
print(f"{'Pages Available to User:':<32}{pagesAvailable}")
print(f"{'Virtual Pages Mapped:':<32}{virtualPagesMapped}")
print('------------------------------')
print(f"{'Page Table Hits:':<32}{pageTableHits}")
print(f"{'Pages from Free:':<32}{pagesFromFree}")
print(f"{'Total Page Faults:':<32}{totalPageFaults}")

print('\nPage Table Usage Per Process:')
print('------------------------------')
for i in range(num_trace_files):
    trace_name = trace_files[i]
    # The number of used entries is simply the size of the Page Table dictionary
    used_entries = len(process_page_tables[i])
    
    # Percentage of total 512K entries used
    process_percent = (used_entries / PTE_ENTRIES_PER_PROCESS) * 100
    
    # Wasted Bytes = (Total Entries - Used Entries) * (PTE Size / 8)
    wasted_bytes = (PTE_ENTRIES_PER_PROCESS - used_entries) * (pte_bits / 8)
    
    print(f"[{i}] {trace_name}:")
    print(f"{'Used Page Table Entries:':<32}{used_entries} ({process_percent:.2f}%)")
    print(f"{'Page Table Wasted:':<32}{wasted_bytes:.0f} bytes")
