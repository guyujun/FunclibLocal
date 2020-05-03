#!/usr/bin/env python
import os
import sys

try:
    os.mkdir('psidb')
except Exception:
    pass

db_path = os.path.join(os.getcwd(), 'psidb/db.fasta')

with open(sys.argv[1], 'r') as f, open(db_path, 'w') as f1:
    lines = f.readlines()
    for line in lines:
        if line.startswith('>'):
            f1.write('\n')
            f1.write(line)
            continue
        else:
            line = line.strip('\n')
            f1.write(line)

os.chdir('psidb')
os.system('makeblastdb -dbtype prot -in db.fasta')

print('End Normally')

os.chdir('../')
os.system(f'psiblast -db {db_path} -query {sys.argv[2]} -evalue 0.001 -num_iterations 3 -out_ascii_pssm result.pssm')
os.system('rm -rf psidb')
