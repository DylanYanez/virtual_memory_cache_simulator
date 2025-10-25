import sys # necessary to read command line arguments
import argparse

# now we need to set those parameters from the given flags
parser = argparse.ArgumentParser(description='Cache Simulator')

# set the flags we will accept
parser.add_argument('-s', type=int, help='Cache Size - KB', dest='cache_size') # (8, 8192) KB
parser.add_argument('-b', type=int, help='Block Size - bytes', dest='block_size') # (8, 64) Bytes
parser.add_argument('-a', type=int, help='Associativity', dest='associativity') # (1, 2, 4, 8, 16)
parser.add_argument('-r', type=int, help='Replacement Policy', dest='replacement_policy') # RR or RND
parser.add_argument('-p', type=int, help='Physical Memory - MB', dest='physical_memory') # 128MB to 4GB
parser.add_argument('-u', type=int, help='% physical mem used by OS', dest='utilization') # 0-100%
parser.add_argument('-n', type=int, help='Instructions / Time Slice', dest='instructions') # 1-All, -1 for All
parser.add_argument('-f', type=int, help='Trace File Name', dest='trace_file') # required 1, up to 3


# parse the parameters
args = parser.parse_args()

cache_size = args.cache_size
if ( 8192 > cache_size < 8):
    print('Cache Size must be between 8 and 8192 MB!')
print(f'{args.cache_size}')

print('Cache Simulator - CS 3853 - Team #17\n')

print('Trace File(s):')
trace_files = {'file1.txt', 'file2.txt', 'file3.txt'}
for file in trace_files:
    print(f'\t{file}')
    
    
print('\n***** Cache Input Parameters *****\n')
cache_parameters = {
    'Cache Size': '512KB',
    'Block Size': '16 bytes',
    'Associativity': '4',
    'Replacement Policy': 'Round Robin',
    'Physical Memory': '1024MB',
    'Percent Memory Used by System': '75.0%',
    'Instructions / Time Slice': '100' 
}

for parameter, value in cache_parameters.items():
    print(f'{parameter}:\t\t{value}')
