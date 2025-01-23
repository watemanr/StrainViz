# **A Manual for Changes in the Git Repository and Usage on the GUIZI Cluster**

---

## **Installing StrainViz on the GUIZI Cluster**

### **1. Download StrainViz via `git`**

I have forked the original StrainViz repository and adapted it to support the SLURM system. It is recommended to clone the repository into the directory: `/home/$USER/Apps`.

```bash
mkdir -p /home/$USER/Apps

cd /home/$USER/Apps

git clone git@github.com:watemanr/StrainViz.git
```

If the GitHub link is inaccessible via CLI, you can alternatively extract the provided `StrainViz.zip` or another compressed file into `/home/$USER/Apps`.

### **2. Update the StrainViz Path in `sub_StrainViz.sh`**

Edit the variable `$StrainViz_path` in the `sub_StrainViz.sh` script to match your installation path. The recommended and default path is `/home/$USER/Apps/StrainViz/`.

### **3. Update Default Queue and Core Number**

Modify the default queue name and core number at the top of `sub_StrainViz.sh` to align with the cluster configuration. Ensure the defaults fit the system’s specifications.

---

## **Workflow for Using StrainViz on the GUIZI Cluster**

### **1. Prepare XYZ Files**

Prepare the XYZ files for the entire ring and its fragments. The folder structure should follow the format below:

```
folder/
├── input/
│   ├── mol_name/
│   │   ├── mol_name-1.xyz
│   │   ├── mol_name-2.xyz
│   │   ├── mol_name-3.xyz
│   │   ├── mol_name-4.xyz
│   └── mol_name.xyz
```

**Rules**:
- The `input` directory must be named as `input`.
- The base name of `mol_name.xyz`, and the folder `mol_name` must share the same name.
- The fragment XYZ files within the `mol_name` folder do not need specific naming conventions, but they must all have a `.xyz` extension. The script will automatically scan the folder and include them.

---

### **2. Navigate to the Working Directory**

Change to the folder containing your input files, for example:

```bash
cd /home/$USER/data/test/test_StrainViz/test_slurm
```

Verify the directory contents:
```bash
[yzhou@master:/home/yzhou/data/test/test_StrainViz/test_slurm] ll
total 18
drwxrwxr-x 3 yzhou yzhou    4 Jan 22 17:15 input
[yzhou@master:/home/yzhou/data/test/test_StrainViz/test_slurm] ll ./input/
total 22
drwxrwxr-x 2 yzhou yzhou   14 Jan 22 17:37 mol
-rw-rw-r-- 1 yzhou yzhou 2136 Jan 22 17:15 mol.xyz
```

---

### **3. Run the `sub_StrainViz.sh` Script**

The default and recommended path for the script is `/home/$USER/Apps/StrainViz`.

To view the usage instructions, run:
```bash
bash /home/$USER/Apps/StrainViz/sub_StrainViz.sh -h
```

**Output:**
```
Usage: /home/$USER/Apps/StrainViz/sub_StrainViz.sh -r <molecule_name> [-N <num_procs>] [-q <queue_name>] [-m <method>] [-h]

Options:
  -r <molecule_name>   Specify the molecule name (required)
  -N <num_procs>       Number of processors (default: 48)
  -q <queue_name>      Queue name for job submission (default: standard)
  -m <method>          Calculation method (optional)
  -h                   Show this help message and exit
```

Run the script as follows:
```bash
bash /home/$USER/Apps/StrainViz/sub_StrainViz.sh -r <molecule_name> -N <core_numbers> -m "<calc_method>"
```

- The `-m` option supports strings instead of a single word. Enclose the entire calculation method in quotes, excluding the `opt` keyword (e.g., `"b3lyp/def2svp em=gd3bj"`).

---

> ⚠️ **Warning:**  
> **Do not** use the `nosymm` keyword, as the script relies on molecule coordinates to follow standard conventions.

---

#### **Example Command**
```bash
bash /home/$USER/Apps/StrainViz/sub_StrainViz.sh -r mol
```

This will submit the job to the default queue (`standard`) using the default number of cores and the default method (`b3lyp/def2svp`).

---

### **4. Download the Results**

The results will be saved in the `output` directory under the same folder where the job was submitted. For example:

```
folder/
├── input/
├── output/
│   ├── mol_name/
│   │   ├── total_force.tcl
│   │   ├── mol_name.xyz
│   │   └── other files...
```

Download the files from the `output` directory to your local machine.

---

### **5. Visualize Results in VMD**

1. Download the following files to the same local directory:
   - `mol.xyz`
   - `total_force.tcl`

2. Open **VMD** (Visualization Molecular Dynamics software).

3. In the **VMD Main** window, navigate to `Extensions > Tk Console`.

4. Change to the local folder in the Tk Console:
   ```bash
   cd /path/to/local/folder
   ```

5. Run the following command in the Tk Console:
   ```tcl
   source total_force.tcl
   ```

This will load `total_force.tcl` and `mol.xyz` into VMD and display the molecular structure with force vectors as a color-coded visualization in the VMD Display window.

---

## **Repository Changes**

### **1. Changes in `StrainViz.bash`**

The original script was designed to run in the location of the script file `StrainViz.bash`. To work with custom paths, such as files in `/repo/input` (e.g., `example-molecule.xyz`) and the directory `example-molecule`, modifications were necessary.

The original script utilized the Gaussian module `gaussian` and the corresponding command `g09` to perform Gaussian calculations, while Python was used to run associated scripts.

To enable execution in a user-defined directory, the initial portion of `StrainViz.bash` was modified as follows:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# $1 is the molecule name, and $2 is a string for calculation method keywords, like "b3lyp/6-31g(d) em=gd3bj"
dir=`pwd`

cd $dir/input/$1

# Get a list of the dummy file names
INPUT_NAMES=()
while IFS=  read -r -d $'\0'; do
	# Remove the leading ./ and the file extension
	INPUT_NAME=${REPLY##*/}
	INPUT_NAME=${INPUT_NAME%.*}
    # Add to the list
	INPUT_NAMES+=("$INPUT_NAME")
done < <(find . -type f -name "*.xyz" -print0)
```

This modification allows calculations to run in a user-defined directory (DIY path).

Additionally:
- The `py3-numpy` module is required to run Python scripts.
- The `Gaussian` module must be loaded to execute `g16`.

All instances of the `python` and `g09` commands in the repository have been updated to `python3` and `g16`, respectively. This change ensures compatibility with updated environments and modules.

Other path-related changes were made throughout the script to ensure compatibility with custom paths.

---

### **2. Changes in `scripts/scripts.py/load_geometry()`**

The following modification was made to handle empty lines in XYZ files gracefully:

```python
def load_geometry(geometry):
	output_lines = open(geometry, 'r').read().splitlines()
	output_lines.pop(0)
	output_lines.pop(0)
	atom_list = []
	for x, line in enumerate(output_lines):
        # Check if the line is empty or contains only whitespace
        if line.strip() == "":
            break  # Stop processing when an empty line is encountered
		print(x, line)
		a = line.split()
		atom_list.append([x+1, a[0], float(a[1]), float(a[2]), float(a[3])])
		
	return atom_list
```

The `break` statement ensures that empty lines at the end of XYZ files do not interfere with the script.

---

### **3. Changes in `scripts/input_gen.py`**

The `periodic_table_dictionary` was embedded directly into the script, eliminating the need to load the file `/home/yzhou/Apps/StrainViz/scripts/periodic_table.txt`.

---

### **4. Changes in `scripts/bond_scripts.py`**

A `header_content` string was added to define the header of the `TCL` file directly in the script, removing the dependency on `/home/yzhou/Apps/StrainViz/scripts/vmd_header.tcl`.

---

### **5. Changes in `scripts/proton_opt.py/create_protonopts()`**

On line 21, the following change was made to avoid a full comparison of elements and XYZ coordinates between the ring XYZ file and fragment XYZ files:

```python
if dummy_atom[1] == base_atom[1] and sum((float(dummy_coord) - float(base_coord))**2 for dummy_coord, base_coord in zip(dummy_atom[2:4], base_atom[2:4])) < 1e-6:
```

This ensures that the comparison uses a distance-based criterion instead of an exact match.

---

### **6. Changes in `scripts/scripts.py/create_key()`**

Atom matching was updated similarly to the above, using a distance-based comparison:

```python
key = []
extra_atoms = []
for line1 in base_atoms:
	for line2 in dummy_atoms:
		# if line1[1:] == line2[1:]:
		if line1[1] == line2[1] and sum((float(dummy_coord) - float(base_coord))**2 for dummy_coord, base_coord in zip(line2[2:], line1[2:])) < 1e-6:
			# print(f"line1: {line1}, line2: {line2}")
			key.append([line2[0], line1[0]])
```

---

### **7. Changes in `scripts/StrainViz.py`**

A distance-based criterion was used to match atoms in the same position. The updated logic is as follows:

```python
missing_atoms = False
for line in load_geometry("input/" + geometry_filename):
    print(f"line: {line}")
    line_in_full_atoms = False
    for full_atom in full_atoms:
        if line[1] == full_atom[0] and sum((float(line_coord) - float(full_coord))**2 for line_coord, full_coord in zip(line[2:], full_atom[1:])) < 1e-6:
            line_in_full_atoms = True
            break
    if line_in_full_atoms == False:
        print(f"line not in full_atoms: {line}")
        missing_atoms = True
        break
    # if line[1:] not in full_atoms:
    #     missing_atoms = True
# print(f"missing_atoms: {missing_atoms}")
if missing_atoms == True:
    print("Base molecule not fully covered. Make more fragments.")
```

This ensures that atoms are matched based on their spatial proximity rather than exact string matches.

---

This manual outlines the workflow for using StrainViz on the GUIZI cluster and the modifications made to the repository to improve compatibility, usability, and robustness. These changes ensure the software can handle custom paths, streamline dependencies, and enhance flexibility in atom matching and file handling.