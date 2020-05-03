#!/usr/bin/env python
import sys
import os

'''
example:
make_flags.py example.pdb 18B,69B,93B 65B,13B
'''

input_pdb = sys.argv[1]
res_to_fix = sys.argv[2]
all_to_mut = sys.argv[3]

with open('refine.flags', 'w') as f:
    line = f'''-use_input_sc
-extrachi_cutoff 5
-ignore_unrecognized_res
-chemical:exclude_patches LowerDNA UpperDNA Cterm_amidation SpecialRotamer VirtualBB ShoveBB VirtualDNAPhosphate VirtualNTerm CTermConnect sc_orbitals pro_hydroxylated_case1 pro_hydroxylated_case2 ser_phosphorylated thr_phosphorylated tyr_phosphorylated tyr_sulfated lys_dimethylated lys_monomethylated lys_trimethylated lys_acetylated glu_carboxylated cys_acetylated tyr_diiodinated N_acetylated C_methylamidated MethylatedProteinCterm
-linmem_ig 10
-ignore_zero_occupancy false
-out:path:pdb refinement
-out:path:score refinement
-in:auto_setup_metals
-s {input_pdb}
-parser:protocol refine.xml
-parser:script_vars res_to_fix={res_to_fix}
-parser:script_vars cst_full_path=bbCA.cst
'''
    f.write(line)


with open('filterscan.flags', 'w') as f:
    line = f'''-use_input_sc
-extrachi_cutoff 5
-ignore_unrecognized_res
-chemical:exclude_patches LowerDNA UpperDNA Cterm_amidation SpecialRotamer VirtualBB ShoveBB VirtualDNAPhosphate VirtualNTerm CTermConnect sc_orbitals pro_hydroxylated_case1 pro_hydroxylated_case2 ser_phosphorylated thr_phosphorylated tyr_phosphorylated tyr_sulfated lys_dimethylated lys_monomethylated lys_trimethylated lys_acetylated glu_carboxylated cys_acetylated tyr_diiodinated N_acetylated C_methylamidated MethylatedProteinCterm
-linmem_ig 10
-ignore_zero_occupancy false
-in:auto_setup_metals
-parser:script_vars current_res={all_to_mut}
-s lowest_energy.pdb
-parser:protocol filterscan.xml
-parser:script_vars res_to_fix={res_to_fix}
-parser:script_vars cst_full_path=bbCA.cst
-parser:script_vars pssm_full_path=result.pssm
'''
    f.write(line)

with open('mutate.flags', 'w') as f:
    line = f'''-use_input_sc
-extrachi_cutoff 5
-ignore_unrecognized_res
-chemical:exclude_patches LowerDNA UpperDNA Cterm_amidation SpecialRotamer VirtualBB ShoveBB VirtualDNAPhosphate VirtualNTerm CTermConnect sc_orbitals pro_hydroxylated_case1 pro_hydroxylated_case2 ser_phosphorylated thr_phosphorylated tyr_phosphorylated tyr_sulfated lys_dimethylated lys_monomethylated lys_trimethylated lys_acetylated glu_carboxylated cys_acetylated tyr_diiodinated N_acetylated C_methylamidated MethylatedProteinCterm
-linmem_ig 10
-ignore_zero_occupancy false
-out:path:pdb output
-out:path:score output
-in:auto_setup_metals
-parser:protocol mutate.xml
-parser:script_vars res_to_fix={res_to_fix}
-parser:script_vars cst_full_path=bbCA.cst
-parser:script_vars all_ress={all_to_mut}
-s lowest_energy.pdb
'''
    f.write(line)


try:
    os.mkdir('refinement')
except Exception:
    pass

try:
    os.mkdir('resfiles')
except Exception:
    pass

try:
    os.mkdir('output')
except Exception:
    pass
