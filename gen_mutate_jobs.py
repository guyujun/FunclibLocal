import itertools
import os
import sys

AA = {
    'G': "GLY",
    'A': "ALA",
    'S': "SER",
    'P': "PRO",
    'V': "VAL",
    'T': "THR",
    'C': "CYS",
    'L': "LEU",
    'I': "ILE",
    'N': "ASN",
    'D': "ASP",
    'Q': "GLN",
    'K': "LYS",
    'E': "GLU",
    'M': "MET",
    'H': "HIS",
    'F': "PHE",
    'R': "ARG",
    'Y': "TYR",
    'W': "TRP",
}

os.chdir('resfiles')
with open('../jobs.list', 'a') as f:
    for resfile in [i for i in os.listdir() if i.endswith(sys.argv[1])]:
        lines = open(resfile, 'r').readlines()
        targets = []
        mutations = []
        ks = []
        Nall = 1
        for l in lines[2:]:
            es = l.strip().split()
            pos = es[0]
            chn = es[1]
            muts = es[3]
            nm = len(muts)
            ks.append(range(nm))
            targets.append(pos + chn)
            mutations.append(muts)

        for ids in itertools.product(*ks):
            tags = ""
            opts = ""
            for n, i in enumerate(ids):
                tags += "%02d" % i
                opts += "target%d=%s " % (n, targets[n])
                opts += "new_res%d=%s " % (n, AA[mutations[n][i]])
            cmd = "rosetta_scripts.mpi.macosclangrelease @mutate.flags -out:suffix _"
            cmd += tags
            cmd += " -parser:script_vars "
            cmd += opts
            print(cmd)
            f.write(cmd+'\n')
