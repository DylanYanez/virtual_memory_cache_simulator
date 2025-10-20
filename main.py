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
