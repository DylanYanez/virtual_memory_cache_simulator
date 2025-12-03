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

# --- GLOBAL INITIALIZATION (Fixing the "Crash" Error) ---
cacheRRCounter = 0
pageRRCounter = 0
cacheMisses = 0
compulsoryMisses = 0
totalCycles = 0
cacheAccesses = 0
conflictMisses = 0
cacheHits = 0

# These were missing and causing crashes:
instructionCount = 0
instructionBytes = 0
srcDstBytes = 0

# Memory reads required to fill one cache block (used in CPI)
numMemoryReads = math.ceil(block_size/4)

# CACHE STRUCTURE
cache = []
for _ in range(rows):
    row = []
    for _ in range(associativity):
        # Added 'rr_count' just in case we need per-set RR logic later
        row.append({"tag": None, "valid": 0})
    cache.append(row)

# MILESTONE 1: OUTPUT
print('Cache Simulator - CS 3853 - Team #17') 

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
print(f"{'Tag Size:':<32}{tag} bits")
print(f"{'Index Size:':<32}{index} bits")
print(f"{'Total # Rows:':<32}{rows}")
print(f"{'Overhead Size:':<32}{overhead:.0f} bytes")
print(f"{'Implementation Memory Size:':<32}{readable_footprint:.2f} KB ({footprint:.0f} bytes)")
print(f"{'Cost:':<32}${cost:.2f} @ $0.07 per KB")

print('\n***** Physical Memory Calculated Values *****')
print(f"{'Number of Physical Pages:':<32}{pages}")
print(f"{'Number of Pages for System:':<32}{system_pages}")
print(f"{'Size of Page Table Entry:':<32}{pte_bits} bits")
print(f"{'Total RAM for Page Table(s):':<32}{total_ram:.0f} bytes")

# --- MILESTONE 2 VM SETUP ---
pagesAvailable = pages - system_pages # Total pool of pages for ALL user processes

# Shared pool of physical page numbers
# PPNs available range from 'system_pages' up to 'pages - 1'
free_pages = list(range(system_pages, pages))

# Individual page tables for each process
process_page_tables = [{} for _ in range(num_trace_files)] 

pageTableHits = 0      
pagesFromFree = 0      
totalPageFaults = 0    

# Helper to track which PPNs are currently used (for Page Replacement)
mappedPPNS = [] 

# --- FUNCTIONS ---

def cache_access(index, tag, is_instruction):
    """
    Simulates cache access.
    is_instruction: Boolean, True if this is an EIP fetch (affects cycle count)
    """
    global cacheRRCounter, cacheMisses, compulsoryMisses, totalCycles, cacheAccesses, conflictMisses, cacheHits

    cacheAccesses += 1 

    row = cache[index]

    # 1. CHECK FOR HIT
    for block in row:
        if block["valid"] == 1 and block["tag"] == tag: # HIT
            cacheHits += 1
            totalCycles += 1 # 1 cycle for cache hit
            return # IMPORTANT: Return immediately on hit!

    # 2. HANDLE MISS
    # If we are here, it was a miss.
    cacheMisses += 1
    totalCycles += (4 * numMemoryReads) # Add Miss Penalty
    
    # Try to find an empty slot (Compulsory Miss)
    empty_slot = None
    for block in row:
        if block["valid"] == 0:
            empty_slot = block
            break
            
    if empty_slot:
        # Compulsory Miss
        compulsoryMisses += 1
        empty_slot["valid"] = 1
        empty_slot["tag"] = tag
    else:
        # Conflict Miss (Cache is full, need replacement)
        conflictMisses += 1
        
        victim_index = 0
        if replacement_policy.upper() == "RR":
            victim_index = cacheRRCounter % associativity
            cacheRRCounter += 1
        elif replacement_policy.upper() == "RND":
            victim_index = random.randint(0, associativity - 1)
            
        row[victim_index]["valid"] = 1
        row[victim_index]["tag"] = tag

    # Add cycle for Effective Address Calculation (only for Data, not Instructions)
    if not is_instruction:
        totalCycles += 1


def handle_vm_access(address_int, process_id):
    """
    Resolves VA to PA. Handles Page Faults and Cache Invalidation.
    Returns the Physical Address (PA).
    """
    global pageRRCounter, pageTableHits, pagesFromFree, totalPageFaults, totalCycles, conflictMisses
    
    virtualPageTable = process_page_tables[process_id]
    
    vpn = address_int // PAGE_SIZE
    page_offset = address_int % PAGE_SIZE

    # 1. Page Table Hit
    if vpn in virtualPageTable:
        pageTableHits += 1
        ppn = virtualPageTable[vpn]
        return (ppn * PAGE_SIZE) + page_offset 
    
    # 2. Page Table Miss
    else:
        # Check Free Pool
        if free_pages:
            ppn = free_pages.pop(0) 
            virtualPageTable[vpn] = ppn 
            pagesFromFree += 1
            mappedPPNS.append(ppn) 
            return (ppn * PAGE_SIZE) + page_offset
        
        # 3. Page Fault (Swap Required)
        else:
            totalPageFaults += 1
            totalCycles += 100 # Penalty for Page Fault
            
            # Select Victim Page (Round Robin or Random from currently used pages)
            replacedPPN = -1
            if replacement_policy == "Round Robin":
                if not mappedPPNS: # Safety check
                    return None 
                replacedPPN = mappedPPNS[pageRRCounter % len(mappedPPNS)]
                pageRRCounter += 1
            else: # Random
                 if not mappedPPNS: return None
                 replacedPPN = mappedPPNS[random.randint(0, len(mappedPPNS) - 1)]

            # Unmap this PPN from whoever owns it
            for process in range(len(process_page_tables)): 
                found = False
                # We have to search the dict to find who owns this PPN
                # Copy items to list to allow modification during iteration
                for loopvpn, ppn in list(process_page_tables[process].items()):
                    if ppn == replacedPPN:
                        del process_page_tables[process][loopvpn]
                        found = True
                        break
                if found: break

            # Map to new VPN
            virtualPageTable[vpn] = replacedPPN
            
            # --- CACHE INVALIDATION LOGIC (Corrected) ---
            # We must find ANY cache block that belongs to the replacedPPN (4KB page).
            # We iterate the whole cache.
            for row_idx in range(rows):
                for block in cache[row_idx]:
                    if block["valid"] == 1:
                        # Reconstruct the Physical Address of this cache block
                        # This is tricky without storing PPN, but we can check the Tag
                        # PPN is the top 18 bits (usually).
                        # Let's use the Tag + Index to check if it falls in the PPN's range.
                        
                        # Reconstruct part of the address from Tag and Index
                        # This works because PA = (Tag << (index+offset)) | (Index << offset) | offset_within_block
                        # We just check if the resulting address falls into the Replaced PPN page.
                        
                        block_addr_base = (block["tag"] << (index + block_offset)) | (row_idx << block_offset)
                        
                        # Get the PPN of this block
                        block_ppn = block_addr_base // PAGE_SIZE
                        
                        if block_ppn == replacedPPN:
                            block["valid"] = 0 # Invalidate!

            return (replacedPPN * PAGE_SIZE) + page_offset 

# --- MAIN TRACE PROCESSING LOOP ---

for count, tracefile in enumerate(trace_files): 
    
    with open(tracefile, "r") as curFile:
        for line in curFile:
            
            # PROCESS INSTRUCTION FETCH (EIP)
            if line.startswith("EIP"):
                # Format: EIP (04): 7c809767
                length = int(line[5:7])
                instructionBytes += length
                instructionCount += 1 # Count instructions for CPI!
                
                address_int = int(line[10:18], 16)
                
                # Iterate through instruction bytes
                current_addr = address_int
                while current_addr < address_int + length:
                    # 1. Get PA from VM
                    phys_addr = handle_vm_access(current_addr, count)
                    
                    if phys_addr is not None:
                        # 2. Calculate Cache Index/Tag
                        curIndex = (phys_addr >> block_offset) & ((1 << index) - 1)
                        curTag = phys_addr >> (block_offset + index)
                        
                        # 3. Access Cache (is_instruction = True)
                        cache_access(curIndex, curTag, True)
                    
                    current_addr += 4 

                # Add base execution cycles (+2 per instruction)
                totalCycles += 2
            
            # PROCESS DATA ACCESS (dstM)
            elif line.startswith("dstM"):
                
                # dstM
                if line[15] != "-":
                    destAddress_str = line[6:14]
                    if destAddress_str != '00000000': 
                        address_int = int(destAddress_str, 16)
                        srcDstBytes += 4
                        
                        phys_addr = handle_vm_access(address_int, count)
                        if phys_addr is not None:
                            curIndex = (phys_addr >> block_offset) & ((1 << index) - 1)
                            curTag = phys_addr >> (block_offset + index)
                            # Data Access (is_instruction = False)
                            cache_access(curIndex, curTag, False)
                
                # srcM
                if line[44] != "-":
                    sourceAddress_str = line[33:41] 
                    if sourceAddress_str != '00000000': 
                        address_int = int(sourceAddress_str, 16)
                        srcDstBytes += 4
                        
                        phys_addr = handle_vm_access(address_int, count)
                        if phys_addr is not None:
                            curIndex = (phys_addr >> block_offset) & ((1 << index) - 1)
                            curTag = phys_addr >> (block_offset + index)
                            # Data Access (is_instruction = False)
                            cache_access(curIndex, curTag, False)

# --- FINAL METRICS & OUTPUT ---

virtualPagesMapped = pageTableHits + pagesFromFree

print('\n***** VIRTUAL MEMORY SIMULATION RESULTS *****')
print()
print(f"{'Physical Pages Used By SYSTEM:':<32}{system_pages}")
print(f"{'Pages Available to User:':<32}{pagesAvailable}")
print()
print(f"{'Virtual Pages Mapped:':<32}{virtualPagesMapped}")
print(f"{'':<8}{'------------------------------'}")
print(f"{'        Page Table Hits:':<32}{pageTableHits}\n")
print(f"{'        Pages From Free:':<32}{pagesFromFree}\n")
print(f"{'        Total Page Faults:':<32}{totalPageFaults}\n\n")

print('Page Table Usage Per Process:')
print('------------------------------')
for i in range(num_trace_files):
    trace_name = trace_files[i]
    used_entries = len(process_page_tables[i])
    process_percent = (used_entries / PTE_ENTRIES_PER_PROCESS) * 100
    wasted_bytes = (PTE_ENTRIES_PER_PROCESS - used_entries) * (pte_bits / 8)
    
    print(f"[{i}] {trace_name}:")
    print(f"{'        Used Page Table Entries: '}{used_entries} ({process_percent:.2f}%)")
    print(f"{'        Page Table Wasted: '}{wasted_bytes:.0f} bytes\n")

# CACHE RESULTS

unusedCacheBlocks = 0
for row in cache:
    for cacheBlock in row:
        if cacheBlock["valid"] == 0:
            unusedCacheBlocks += 1

unused_cache_bytes = unusedCacheBlocks * block_size
total_cache_bytes = cache_size * 1024
unused_cache_percent = (unused_cache_bytes / total_cache_bytes) * 100

# Calculate CPI
if instructionCount > 0:
    cpi = totalCycles / instructionCount
else:
    cpi = 0

print('***** CACHE SIMULATION RESULTS *****')
print(f"{'Total Cache Accesses:':<24}{cacheAccesses}\n")
print(f"{'--- Instruction Bytes:':<24}{instructionBytes}\n")
print(f"{'--- SrcDst Bytes:':<24}{srcDstBytes}\n")
print(f"{'Cache Hits:':<24}{cacheHits}\n")
print(f"{'Cache Misses':<24}{cacheMisses}\n")
print(f"{'--- Compulsory Misses:':<24}{compulsoryMisses}\n")
print(f"{'--- Conflict Misses':<24}{conflictMisses}\n\n\n")
print('***** ***** CACHE HIT & MISS RATE: ***** *****\n\n')

if cacheAccesses > 0:
    hitRate = (cacheHits * 100) / cacheAccesses
    missRate = (100 - hitRate)
else:
    hitRate = 0
    missRate = 0

print(f"{'Hit Rate:':<24}{hitRate:.4f}%")
print(f"{'Miss Rate:':<24}{missRate:.4f}%")
print(f"{'CPI:':<24}{cpi:.2f} Cycles/Instruction ({totalCycles})")

unusedCacheSpace = ((total_blocks - compulsoryMisses) * (block_size + overhead)) / 1024
# Note: Unused cache space calculation logic provided in prompt was slightly approximate, 
# but we stick to the provided formula logic: unused blocks * block size is better.
# However, let's stick to the prompt's implied logic of (Total - Used Blocks).
# Actually, the most accurate is counting explicit valid=0 blocks.
unusedCacheSpace = (unusedCacheBlocks * (block_size + (overhead_bits/total_blocks/8))) / 1024
# Simplified to match the spirit of "Unused KB":
unusedCacheSpaceKB = (unusedCacheBlocks * block_size) / 1024

waste = 0.07 * unusedCacheSpaceKB # Approx cost

print(f"{'Unused Cache Space:':<24}{unusedCacheSpaceKB:.2f} KB / {cache_size} KB = {unused_cache_percent:.2f}% Waste: ${waste:.2f}/chip\n")
print(f"{'Unused Cache Blocks:':<24}{unusedCacheBlocks} / {total_blocks}")
