#!bin/bash
set -e

DEBUG=true
defalut_NProcShared=48
param2=${2:-"b3lyp/def2svp"} # default keyword is "b3lyp/def2svp"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# $1 is the name of the molecule and $2 is str: keyword for the calculation method like "b3lyp/6-31g(d) em=gd3bj"
dir=`pwd`

if [ "$DEBUG" = true ]; then
    echo $SCRIPT_DIR
    echo $dir
    echo $defalut_NProcShared
    echo $param2
fi


cd $dir/input/$1

# Get a list of the dummy file names
INPUT_NAMES=()
while IFS=  read -r -d $'\0'; do
	# Remove the leading ./ and following .ext
	INPUT_NAME=${REPLY##*/}
	INPUT_NAME=${INPUT_NAME%.*}
    # Add to list
	INPUT_NAMES+=("$INPUT_NAME")
    echo $INPUT_NAME
done < <(find . -type f -name "*.xyz" -print0)

if [ "$DEBUG" = true ]; then
echo "${INPUT_NAMES[@]}"
fi

cd $dir
# # Create _protonopt.inp files to optimize the proton in Gaussian from the dummy .xyz files

### yzhou: load py3-numpy module to run python3
module load py3-numpy

if [ "$DEBUG" = true ]; then
echo $1
echo $defalut_NProcShared
echo "$param2"
fi

python3 $SCRIPT_DIR/scripts/proton_opt.py $1 $defalut_NProcShared "$param2"
echo "[$(date +"%Y-%m-%d %T")] Proton optimization files created."


cd $dir/input/$1
fileend="_protonopt"
# Run the _protonopt.inp files in Gaussian to get _protonopt.out files
### yzhou: change name of module to Gaussian

# module load gaussian
module load Gaussian

# change g09 to g16
for file in "${INPUT_NAMES[@]}"; do
    g16 < "$file$fileend.inp" > "$file$fileend.out" || echo "[$(date +"%Y-%m-%d %T")] $file proton optimization failed."
    echo "[$(date +"%Y-%m-%d %T")] $file protons optimized."
done

cd $dir
# Create .inp files to calculate the energy in Gaussian from the _protonopt.out files and 
# deletes the protonopt files
python3 $SCRIPT_DIR/scripts/input_gen.py $1 $defalut_NProcShared "$param2"
echo "[$(date +"%Y-%m-%d %T")] Gaussian input files created."


cd $dir/input/$1
# Run the .inp files in Gaussian to get .out files
for file in "${INPUT_NAMES[@]}"; do
    g16 < "$file.inp" > "$file.out" || echo "[$(date +"%Y-%m-%d %T")] $file energy calculation failed."
    echo "[$(date +"%Y-%m-%d %T")] $file Gaussian run done."
done

cd $dir
mkdir -p output/$1
# Calculates the strain and creates .tcl files to be visualized in VMD
python3 $SCRIPT_DIR/scripts/StrainViz.py $1
cp $dir/input/$1.xyz $dir/output/$1
echo "[$(date +"%Y-%m-%d %T")] StrainViz analysis finished."
