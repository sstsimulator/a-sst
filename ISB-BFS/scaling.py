#!/usr/bin/env python3
import os
import sys

# Full
sizes   = range(16,25)
threads = [1]
nodes   = [4,9,16,25,36,49,64]

versions = ['exponential', 'polynomial', 'trace']

def supported():
    print(f'Supported versions are: {versions}')

if (len(sys.argv) < 2):
    print("Usage: ./scaling <version>")
    supported()
    sys.exit(1)

version = sys.argv[1]
if version not in versions:
    supported()
    sys.exit(1)

print('nodes ranks threads_per_rank scale time(ms)')
simtime_ms = []
for n in nodes:
    for th in threads:
        for sz in sizes:
            cmd = f'sst cori-simple.py --model-options="{n} {th} {sz} {version}" 2>/dev/null | tail -n 1 > tmp.out'
            os.system(cmd)
            with open('tmp.out') as file:
                for ln in file.readlines():
                    time = float(ln.strip().split()[5])
                    unit = ln.strip().split()[6]
                    if (unit == 's'):
                        time = time * 1000
                    elif (unit == 'Ks'):
                        time = time * 1000 * 1000
                    elif (unit != 'ms'):
                        print(f"unexpected time unit: {unit}")

                    # Right now, nodes = ranks (1 rank per node)
                    print(f'{n} {n} {th} {sz} {time:.2f}')
                    break # shouldn't need, just in case

