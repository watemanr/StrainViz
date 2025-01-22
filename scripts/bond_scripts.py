from scripts import get_atom_coords, get_connectivity_data, load_geometry, create_key
import os
import copy

# Define the header content as a multi-line string
header_content = """\
# Change bond radii and various resolution parameters
mol representation cpk 0.8 0.0 30 5
mol representation bonds 0.2 30

# Change the drawing method of the first graphical representation to CPK
mol modstyle 0 top cpk
axes location off
display cuedensity 0.25
# Color only H atoms white
mol modselect 0 top {name H}
# Change the color of the graphical representation 0 to white
color change rgb 0 1.00 1.00 1.00
mol modcolor 0 top {colorid 0}
# The background should be white ("blue" has the colorID 0, which we have changed to white)
color Display Background blue

# Define the other colorIDs
color change rgb   1  0.000000  1.000000  0.000000
color change rgb   2  0.062500  1.000000  0.000000
color change rgb   3  0.125000  1.000000  0.000000
color change rgb   4  0.187500  1.000000  0.000000
color change rgb   5  0.250000  1.000000  0.000000
color change rgb   6  0.312500  1.000000  0.000000
color change rgb   7  0.375000  1.000000  0.000000
color change rgb   8  0.437500  1.000000  0.000000
color change rgb   9  0.500000  1.000000  0.000000
color change rgb  10  0.562500  1.000000  0.000000
color change rgb  11  0.625000  1.000000  0.000000
color change rgb  12  0.687500  1.000000  0.000000
color change rgb  13  0.750000  1.000000  0.000000
color change rgb  14  0.812500  1.000000  0.000000
color change rgb  15  0.875000  1.000000  0.000000
color change rgb  16  0.937500  1.000000  0.000000
color change rgb  17  1.000000  0.937500  0.000000
color change rgb  18  1.000000  0.875000  0.000000
color change rgb  19  1.000000  0.812500  0.000000
color change rgb  20  1.000000  0.750000  0.000000
color change rgb  21  1.000000  0.687500  0.000000
color change rgb  22  1.000000  0.625000  0.000000
color change rgb  23  1.000000  0.562500  0.000000
color change rgb  24  1.000000  0.500000  0.000000
color change rgb  25  1.000000  0.437500  0.000000
color change rgb  26  1.000000  0.375000  0.000000
color change rgb  27  1.000000  0.312500  0.000000
color change rgb  28  1.000000  0.250000  0.000000
color change rgb  29  1.000000  0.187500  0.000000
color change rgb  30  1.000000  0.125000  0.000000
color change rgb  31  1.000000  0.062500  0.000000
color change rgb  32  1.000000  0.000000  0.000000

# Adding a representation with the appropriate colorID for each bond
"""

""" Maps the force values from the output file onto the original geometry .xyz file by digesting 
the output files and writing .tcl scripts to by viewed in VMD
"""
def map_forces(geometry, force_output):
	#Parse file for values
	bond_forces, angle_forces, dihedral_forces = force_parse(geometry[:-4] + "/" + force_output)
	# print(bond_forces)
	bond_atoms = []
	for line in bond_forces:
		bond_atoms.append(bond_forces[1])
	# print(f"bond atoms:{bond_atoms}")
	#Use the base geometry and unoptimized dummy geometry to create a key
	key = create_key(load_geometry(geometry), load_geometry(geometry[:-4] + "/" + os.path.splitext(force_output)[0] + ".xyz"), bond_atoms)
	
	# print(f"key:{key}")
	mapped_bond_forces = translate_forces(bond_forces, key)
	# print(mapped_bond_forces)
	mapped_angle_forces = translate_forces(angle_forces, key)
	mapped_dihedral_forces = translate_forces(dihedral_forces, key)
	
	copy_bond_forces = copy.deepcopy(mapped_bond_forces)
	
	#Makes a list of bonds
	bonds = []
	for line in mapped_bond_forces:
		bonds.append(line[1])
	
	compressed_angle_forces = compress_forces(bonds, mapped_angle_forces)
	compressed_dihedral_forces = compress_forces(bonds, mapped_dihedral_forces)
	
	copy_angle_forces = copy.deepcopy(compressed_angle_forces)
	copy_dihedral_forces = copy.deepcopy(compressed_dihedral_forces)
	
	bond_forces_vmd, bond_min, bond_max = vmd_norm(mapped_bond_forces)
	angle_forces_vmd, angle_min, angle_max = vmd_norm(compressed_angle_forces)
	dihedral_forces_vmd, dihedral_min, dihedral_max = vmd_norm(compressed_dihedral_forces)
	
	raw_output_writer(geometry[6:-4] + "/bond_" + os.path.splitext(force_output)[0] + ".txt", copy_bond_forces)
	vmd_writer(geometry[6:-4] + "/bond_" + os.path.splitext(force_output)[0] + ".tcl", bond_forces_vmd, geometry[6:], bond_min, bond_max)
	# vmd_writer(geometry[6:-4] + "/bond_" + os.path.splitext(force_output)[0] + ".tcl", bond_forces_vmd, geometry[6:], bond_min, bond_max, "scripts/vmd_header.tcl")
	raw_output_writer(geometry[6:-4] + "/angle_" + os.path.splitext(force_output)[0] + ".txt", copy_angle_forces)
	vmd_writer(geometry[6:-4] + "/angle_" + os.path.splitext(force_output)[0] + ".tcl", angle_forces_vmd, geometry[6:], angle_min, angle_max)
	# vmd_writer(geometry[6:-4] + "/angle_" + os.path.splitext(force_output)[0] + ".tcl", angle_forces_vmd, geometry[6:], angle_min, angle_max, "scripts/vmd_header.tcl")
	raw_output_writer(geometry[6:-4] + "/dihedral_" + os.path.splitext(force_output)[0] + ".txt", copy_dihedral_forces)
	vmd_writer(geometry[6:-4] + "/dihedral_" + os.path.splitext(force_output)[0] + ".tcl", dihedral_forces_vmd, geometry[6:], dihedral_min, dihedral_max)	
	# vmd_writer(geometry[6:-4] + "/dihedral_" + os.path.splitext(force_output)[0] + ".tcl", dihedral_forces_vmd, geometry[6:], dihedral_min, dihedral_max, "scripts/vmd_header.tcl")	

	return copy_bond_forces, copy_angle_forces, copy_dihedral_forces

""" Use the format atoms, bond_forces, angle_forces, dihedral_forces = force_parse("outputfile.out") 
when calling this function. Returns lists of bond, angle, and dihedral forces.
"""
def force_parse(file):
	#Read file into python and format into list
	output_lines = open(file,'r').read().splitlines()

	#Initialize needed variables
	read_line = False
	force_data = [[]]
	force_list = []
		
	#Get first force constants
	x = 0
	for line in output_lines:
		if '      Item               Value     Threshold  Converged?' in line and read_line == True:
			read_line = False
			force_data.append([])
			x += 1
			continue
		if '                              (Linear)    (Quad)   (Total)' in line:
			read_line = True
			continue
		if read_line == True:
			force_data[x].append(line.split())
	
	force_data.pop()
	force_data.pop()
	
	#Get energy at each step
	step_energy = []
	for line in output_lines:
		if 'SCF Done:' in line:
			step_energy.append(float(line.split()[4]))
	
	#Get energy change at each step
	step_energy_change = []
	for index, energy in enumerate(step_energy[:-1]):
		step_energy_change.append(step_energy[index+1]-step_energy[index])

	#Check for increase in step energy
	for line in step_energy_change:
		if line > 0:
			print("Positive enegy change in "+file)
			
	#Get predicted change in energy for the step
	pred_step_energy_change = []
	for set in force_data:
		energy = 0
		for line in set:
			energy += float(line[2])*float(line[5])
		pred_step_energy_change.append(energy)
	
	#Create scaling factor for each energy step
	scale_factor = []
	for index, energy in enumerate(step_energy_change[:len(pred_step_energy_change)]):
		if pred_step_energy_change[index] == 0:
			scale_factor.append(0)
		else:
			scale_factor.append(-energy/pred_step_energy_change[index])

	#Get connectivity data
	connectivity_data = get_connectivity_data(output_lines)
	
	for index, line in enumerate(connectivity_data):
		line.append(0)
		for i, set in enumerate(force_data):
			line[-1] += float(set[index][2])*float(set[index][5])*scale_factor[i]
	
	#Reformat into list of [force, coords]
	for line in connectivity_data:
		force_list.append([line[-1], line[:-1]])
	
	#Split into bond, angle, and dihedral forces
	bond_forces = []
	angle_forces = []
	dihedral_forces = []
	for line in force_list:
		if len(line[1]) == 2:
			bond_forces.append(line)
		if len(line[1]) == 3:
			angle_forces.append(line)
		if len(line[1]) == 4:
			dihedral_forces.append(line)
		if len(line[1]) == 5:
			angle_forces.append([line[0],line[1][:2]])
	
	#Return the bond, angle, and dihedral forces as lists
	return bond_forces, angle_forces, dihedral_forces

""" Takes the forces and translates the atom numbers to correspond to the base geometry.
"""
def translate_forces(forces, key):
	forces_raw = []
	for x, a in enumerate(forces):
		forces_raw.append([a[0], []])
		for c in a[1]:
			for b in key:
				if int(c) == b[0]:
					forces_raw[x][1].append(b[1])

	new_forces = []
	for line in forces_raw:
		if len(line[1]) == len(forces[0][1]):
			new_forces.append(line)

	return new_forces

""" Use the format norm_forces = normalize(forces) when calling this function.
Returns a force matrix that is normalized between 1 and 32 for VMD colours.
"""
def vmd_norm(force_values):
	norm_values = []
	for line in force_values:
		norm_values.append(line[0])

	minimum = copy.deepcopy(min(norm_values))
	maximum = copy.deepcopy(max(norm_values))

	norm_min = min(norm_values)
	for i in range(len(norm_values)):
		norm_values[i] -= norm_min

	norm_max = max(norm_values)/31
	for i in range(len(norm_values)):
		norm_values[i] /= norm_max
		norm_values[i] += 1
		norm_values[i] = int(norm_values[i])
		
	norm_force_values = force_values
	for i in range(len(norm_force_values)):
		norm_force_values[i][0] = norm_values[i]
		
	return norm_force_values, minimum, maximum

""" Use the format vmd_writer("name of output.tcl", "list of normalized forces 
and the bonds they belong to", "name of geometry.xyz")
Writes the script that you can then run in the VMD Tk Console using "source script.tcl"
"""
def vmd_writer(script_name, bond_colors, geometry_filename, min, max, header=header_content):
	script = open('output/' + script_name, "w")
	script.write("# Minimum value: %s\n# Maximum value: %s\n\n" % (min*627.509, max*627.509))
	script.write("# Load a molecule\nmol new %s\n\n" % (geometry_filename))
	# with open(header) as script_header:
	# 	for line in script_header:
	# 		script.write(line)
	script.write(header_content)
	script.write("\n")
	for index, line in enumerate(bond_colors):
		script.write("mol addrep top\n")
		script.write("mol modstyle %s top bonds\n" % (index+1))
		script.write("mol modcolor %s top {colorid %s}\n" % (index+1,line[0]))
		script.write("mol modselect %s top {index %s %s}\n\n" % (index+1,int(line[1][0])-1,int(line[1][1])-1))

def raw_output_writer(script_name, forces):
	output = open('output/' + script_name, "w")
	for line in forces:
		for text in line:
			output.write(str(text) + " ")
		output.write("\n")

""" Use the format compressed_forces = compress_forces(bond list, angle or dihedral 
force list)
Because multiple bonds take part in a single angle or dihedral strain, this sums
the force contribution for each bond.
"""
def compress_forces(bonds, forces):
	force_list = []
	for bond in bonds:
		for force in forces:
			if bond[0] in force[1] and bond[1] in force[1]:
				force_list.append([force[0]/(len(force[1])-1), [bond[0],bond[1]]])
	forces_compressed = []
	for bond in bonds:
		forces_compressed.append([0, bond])
	for bond in forces_compressed:
		for x in force_list:
			if bond[1] == x[1]:
				bond[0] += x[0]
	return forces_compressed

""" This function combines all the dummies into a single picture. Forces is a list with 
the format forces[0] = [force, [c1, c2]]"""
def combine_dummies(forces, geometry, force_type):

	#Make a bond list
	bond_list = []
	for line in forces:
		if line[1] in bond_list:
			continue
		else:
			bond_list.append(line[1])
	
	#Now make the new force list
	new_forces = []
	for line in bond_list:
		new_forces.append([0, line])
	
	#Average the forces for each bond
	for bond in new_forces:
		x = 0
		for line in forces:
			if bond[1] == line[1]:
				bond[0] += line[0]
				x += 1
		bond[0] /= x
	
	output_forces = copy.deepcopy(new_forces)
	raw_output_writer(geometry[:-4] + "/" + force_type + "_total.txt", output_forces)

	#Write the forces to a .tcl script
	new_forces_vmd, scale_min, scale_max = vmd_norm(new_forces)
	vmd_writer(geometry[:-4] + "/" + force_type + "_total.tcl", new_forces_vmd, geometry, scale_min, scale_max)
	# vmd_writer(geometry[:-4] + "/" + force_type + "_total.tcl", new_forces_vmd, geometry, scale_min, scale_max, "scripts/vmd_header.tcl")

	return output_forces
	
""" This function combines all the dummies into a single picture. Forces is a list with 
the format forces[0] = [force, [c1, c2]]"""
def combine_force_types(forces, geometry):

	#Make a bond list
	bond_list = []
	for line in forces:
		if line[1] in bond_list:
			continue
		else:
			bond_list.append(line[1])
	
	#Now make the new force list
	new_forces = []
	for line in bond_list:
		new_forces.append([0, line])
	
	#Average the forces for each bond
	for bond in new_forces:
		for line in forces:
			if bond[1] == line[1]:
				bond[0] += line[0]
	
	#Write the forces to a .tcl script
	raw_output_writer(geometry[:-4] + "/total_force.txt", new_forces)
	new_forces_vmd, scale_min, scale_max = vmd_norm(new_forces)
	vmd_writer(geometry[:-4] + "/total_force.tcl", new_forces_vmd, geometry, scale_min, scale_max)
	# vmd_writer(geometry[:-4] + "/total_force.tcl", new_forces_vmd, geometry, scale_min, scale_max, "scripts/vmd_header.tcl")