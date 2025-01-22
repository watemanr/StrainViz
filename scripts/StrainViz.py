from scripts import *
from bond_scripts import *
import os
import sys

geometry_filename = sys.argv[1] + ".xyz"
		
full_atoms = []
full_bond_forces = []
full_angle_forces = []
full_dihedral_forces = []
full_key = []
fragment_nixlist = []
for file in os.listdir("input/" + geometry_filename[:-4]):
    if file.endswith(".out"):
        bond, angle, dihedral = map_forces("input/" + geometry_filename, file)
        for energy in (bond+angle+dihedral):
            if energy[0] < 0:
                fragment_nixlist.append(file)
                print(file + " resulted in negative energies.")
                break
        for line in bond:
            full_bond_forces.append(line)
        for line in angle:
            full_angle_forces.append(line)
        for line in dihedral:
            full_dihedral_forces.append(line)
    if file.endswith(".xyz"):
        for line in load_geometry("input/" + geometry_filename[:-4] + "/" + file):
            full_atoms.append(line[1:])

averaged_bond_forces = combine_dummies(full_bond_forces, geometry_filename, "bond")
averaged_angle_forces = combine_dummies(full_angle_forces, geometry_filename, "angle")
averaged_dihedral_forces = combine_dummies(full_dihedral_forces, geometry_filename, "dihedral")

missing_atoms = False
for line in load_geometry("input/" + geometry_filename):
    # print(f"line: {line}")
    line_in_full_atoms = False
    for full_atom in full_atoms:
        if line[1] == full_atom[0] and sum((float(line_coord) - float(full_coord))**2 for line_coord, full_coord in zip(line[2:], full_atom[1:])) < 1e-6:
            line_in_full_atoms = True
            break
    if line_in_full_atoms == False:
        # print(f"line not in full_atoms: {line}")
        missing_atoms = True
        break
    # if line[1:] not in full_atoms:
    #     missing_atoms = True
# print(f"missing_atoms: {missing_atoms}")
if missing_atoms == True:
    print("Base molecule not fully covered. Make more fragments.")

total_forces = averaged_bond_forces + averaged_angle_forces + averaged_dihedral_forces
combine_force_types(total_forces, geometry_filename)

print_total(total_forces, "Total strain")
print_total(averaged_bond_forces, "Bond strain")
print_total(averaged_angle_forces, "Angle strain")
print_total(averaged_dihedral_forces, "Dihedral strain")