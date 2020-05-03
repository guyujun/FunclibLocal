#!/bin/sh

pdb=$1
lines=`wc $pdb | awk '{print $1}'`;
constraint_func="HARMONIC 0 1" # harmonic constraint mean=0 std=1
constraint_type="CoordinateConstraint" #constraint type
root_aa=`awk '$1=="ATOM" && $3=="CA"{print substr($0, 23, 4)}' $pdb  | head -1`
root_aa_chain=`awk '$1=="ATOM" && $3=="CA"{print substr($0, 22, 1)}' $pdb | head -1 `
root="CA ${root_aa}${root_aa_chain}" #the atom, relative to which the constraints are computed


#echo $pdb $lines

for i in `seq 1 $lines`; do
	if [ "$(awk 'NR=='$i' && ($1=="ATOM" || $1=="HETATM") && $3=="CA"{print}' $pdb)" ];then
		x=`awk 'NR=='$i'{print substr($0, 31, 8)}' $pdb`
		y=`awk 'NR=='$i'{print substr($0, 39, 8)}' $pdb`
		z=`awk 'NR=='$i'{print substr($0, 47, 8)}' $pdb`
		atom=`awk 'NR=='$i'{print $3}' $pdb`
		res_num=`awk 'NR=='$i'{print substr($0, 23, 4)}' $pdb`
		chain=`awk 'NR=='$i'{print substr($0, 22, 1)}' $pdb`
		echo $constraint_type $atom ${res_num}${chain} $root $x $y $z $constraint_func
	fi
done
