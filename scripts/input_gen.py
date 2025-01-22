import os
import sys

# Definitions

""" This function uses the output from the proton optimization to create a Gaussian input 
file for the strain calculation
"""

# Periodic table dictionary with atomic number as key and element symbol as value
periodic_table = {'1': 'H', '2': 'He', '3': 'Li', '4': 'Be', '5': 'B', '6': 'C', '7': 'N', '8': 'O', '9': 'F', '10': 'Ne', '11': 'Na', '12': 'Mg', '13': 'Al', '14': 'Si', '15': 'P', '16': 'S', '17': 'Cl', '18': 'Ar', '19': 'K', '20': 'Ca', '21': 'Sc', '22': 'Ti', '23': 'V', '24': 'Cr', '25': 'Mn', '26': 'Fe', '27': 'Co', '28': 'Ni', '29': 'Cu', '30': 'Zn', '31': 'Ga', '32': 'Ge', '33': 'As', '34': 'Se', '35': 'Br', '36': 'Kr', '37': 'Rb', '38': 'Sr', '39': 'Y', '40': 'Zr', '41': 'Nb', '42': 'Mo', '43': 'Tc', '44': 'Ru', '45': 'Rh', '46': 'Pd', '47': 'Ag', '48': 'Cd', '49': 'In', '50': 'Sn', '51': 'Sb', '52': 'Te', '53': 'I', '54': 'Xe'}

def create_input(file, level):
	output_lines = open(file,'r').read().splitlines()
	
	read_line = False
	
	for line in output_lines:
		if ' Rotational constants (GHZ):' in line and read_line == True:
			read_line = False
			continue
		if ' Number     Number       Type             X           Y           Z' in line:
			coordinates = []
			read_line = True
			continue
		if read_line == True:
			coordinates.append(line.split())
	
	coordinates.pop()
	coordinates.pop(0)
	
	# periodic_table_text = open("/home/yzhou/Apps/StrainViz/scripts/periodic_table.txt",'r').read().splitlines()
	# periodic_table = {}
	# for element in periodic_table_text:
	# 	periodic_table[element.split()[0]] = element.split()[1]

	script = open(file[:-14] + ".inp", "w")
	script.write("%NProcShared=" + sys.argv[2] + "\n#n " + level + " opt=rfo\n\n")
	script.write(" geometry optimization\n\n0 1\n")
	for atom in coordinates:
		script.write("%s\t%s\t%s\t%s\t" % (periodic_table[atom[1]], atom[3], atom[4], atom[5]))
		script.write("\n")
	script.write("\n")
	
	os.remove(file)
	os.remove(os.path.splitext(file)[0] + ".inp")

# Execution

level = sys.argv[3]
fragments = []
fragment_folder = "input/" + sys.argv[1] + "/"
for file in os.listdir(fragment_folder):
    if file.endswith("protonopt.out"):
        fragments.append(fragment_folder + file)

for file in fragments:
    create_input(file, level)