import argparse

# now we need to set those parameters from the given flags
parser = argparse.ArgumentParser(description='Cache Simulator')

# set the flags we will accept
parser.add_argument('-s', type=int, help='Cache Size - KB', dest='cache_size') # (8, 8192) KB
parser.add_argument('-b', type=int, help='Block Size - bytes', dest='block_size') # (8, 64) Bytes
parser.add_argument('-a', type=int, help='Associativity', dest='associativity') # (1, 2, 4, 8, 16)
parser.add_argument('-r', type=str, help='Replacement Policy', dest='replacement_policy') # RR or RND (0 for RR, 1 for RND)
parser.add_argument('-p', type=int, help='Physical Memory - MB', dest='physical_memory') # 128MB to 4GB (4096MB)
parser.add_argument('-u', type=int, help='% physical mem used by OS', dest='utilization') # 0-100%
parser.add_argument('-n', type=int, help='Instructions / Time Slice', dest='instructions') # 1-All, -1 for All
parser.add_argument('-f', type=str, help='Trace File Name', dest='trace_file', action='append') # required 1, up to 3


# parse the parameters
args = parser.parse_args()

# error trapping

# Cache Size (-s) - KB (8, 8192)
cache_size = args.cache_size
if cache_size is None:
    print('Error: Cache Size (-s) is required!')
    sys.exit(1)
if not (8 <= cache_size <= 8192):
    print('Error: Cache Size must be between 8 and 8192 KB!')
    sys.exit(1)

# Block Size (-b) - bytes (8, 64)
block_size = args.block_size
if block_size is None:
    print('Error: Block Size (-b) is required!')
    sys.exit(1)
if not (8 <= block_size <= 64):
    print('Error: Block Size must be between 8 and 64 bytes!')
    sys.exit(1)
if (block_size & (block_size - 1)) != 0: # Check power of 2
    print('Error: Block Size must be a power of 2!')
    sys.exit(1)

# Associativity (-a) (1, 2, 4, 8, 16)
associativity = args.associativity
valid_associativity = {1, 2, 4, 8, 16}
if associativity is None:
    print('Error: Associativity (-a) is required!')
    sys.exit(1)
if associativity not in valid_associativity:
    print('Error: Associativity must be 1, 2, 4, 8, or 16!')
    sys.exit(1)

# Replacement Policy (-r) (RR=0 or RND=1)
replacement_policy = args.replacement_policy
if replacement_policy is None:
    print('Error: Replacement Policy (-r) is required!')
    sys.exit(1)
if replacement_policy not in {'RR', 'RND'}:
    print('Error: Replacement Policy must be RR (Round Robin) or RND (Random)!')
    sys.exit(1)

# Physical Memory (-p) - MB (128, 4096)
physical_memory = args.physical_memory
if physical_memory is None:
    print('Error: Physical Memory (-p) is required!')
    sys.exit(1)
if not (128 <= physical_memory <= 4096):
    print('Error: Physical Memory must be between 128 and 4096 MB!')
    sys.exit(1)
if (physical_memory & (physical_memory - 1)) != 0: # Check power of 2
    print('Error: Physical Memory must be a power of 2!')
    sys.exit(1)

# % physical mem used by OS (-u) (0-100)
utilization = args.utilization
if utilization is None:
    print('Error: Utilization (-u) is required!')
    sys.exit(1)
if not (0 <= utilization <= 100):
    print('Error: Utilization must be between 0 and 100%!')
    sys.exit(1)

# Instructions / Time Slice (-n) (1-All, -1 for All)
instructions = args.instructions
if instructions is None:
    print('Error: Instructions (-n) is required!')
    sys.exit(1)
if not (instructions == -1 or instructions >= 1):
    print('Error: Instructions / Time Slice must be -1 or a positive integer!')
    sys.exit(1)

# Trace File Name (-f) (1, up to 3)
trace_files = args.trace_file
num_trace_files = len(args.trace_file)
if not trace_files:
    print('Error: At least one Trace File (-f) is required!')
    sys.exit(1)
num_trace_files = len(trace_files)
if not (1 <= num_trace_files <= 3):
    print(f'Error: Must specify between 1 and 3 Trace Files. You provided {num_trace_files}.')
    sys.exit(1)


print('Cache Simulator - CS 3853 - Team #17\n')
    
print('\n***** Cache Input Parameters *****\n')
instructions_str = 'All' if instructions == -1 else str(instructions)

cache_parameters = {
    'Cache Size': f'{cache_size} KB',
    'Block Size': f'{block_size} bytes',
    'Associativity': str(associativity),
    'Replacement Policy': replacement_policy,
    'Physical Memory': f'{physical_memory} MB',
    'Percent Memory Used by System': f'{utilization}.0%',
    'Instructions / Time Slice': instructions_str
}

for parameter, value in cache_parameters.items():
    spaces = '\t' if len(parameter) > 15 else '\t\t'
    print(f'{parameter}:{spaces}{value}')


print('\nTrace File(s):')
for file in trace_files:
    print(f'\t{file}')
