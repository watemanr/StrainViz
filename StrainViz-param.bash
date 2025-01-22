#!bin/bash
set -e

DEBUG=false
default_NProcShared=48
calc_method="b3lyp/def2svp"
res=""

# 打印帮助信息
function print_help() {
  echo "Usage: $0 -r <mol> [-N <num_procs>] [-m <method>] [-h]"
  echo ""
  echo "Options:"
  echo "  -r <mol>       Specify the molecule name (required)"
  echo "  -N <num_procs> Number of processors (default: 48)"
  echo "  -m <method>    Quantum chemistry method (default: b3lyp/def2svp)"
  echo "  -h             Show this help message and exit"
  exit 0
}

# 解析命令行参数
while getopts "N:m:r:h" opt; do
  case $opt in
    N) default_NProcShared="$OPTARG" ;;  # 设置 -N 的值
    m) calc_method="$OPTARG" ;;               # 设置 -m 的值
    r) res="$OPTARG" ;;                  # 设置 -r 的值（必填）
    h) print_help ;;                     # 显示帮助信息
    *) echo "Usage: $0 -r <mol> [-N <num_procs>] [-m <calc_method>]"; exit 1 ;;
  esac
done

# 检查必填参数 -r 是否提供
if [[ -z "$res" ]]; then
  echo "Error: -r <mol> is required."
  echo "Usage: $0 -r <mol> [-N <num_procs>] [-m <calc_method>]"
  exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# $res is the name of the molecule and $2 is str: keyword for the calculation method like "b3lyp/6-31g(d) em=gd3bj"
dir=`pwd`

if [ "$DEBUG" = true ]; then
    echo $SCRIPT_DIR
    echo $dir
    echo $default_NProcShared
    echo $calc_method
fi


cd $dir/input/$res

# Get a list of the dummy file names
INPUT_NAMES=()
while IFS=  read -r -d $'\0'; do
	# Remove the leading ./ and following .ext
	INPUT_NAME=${REPLY##*/}
	INPUT_NAME=${INPUT_NAME%.*}
    # Add to list
	INPUT_NAMES+=("$INPUT_NAME")
    # echo $INPUT_NAME
done < <(find . -type f -name "*.xyz" -print0)

if [ "$DEBUG" = true ]; then
echo "${INPUT_NAMES[@]}"
fi

cd $dir
# # Create _protonopt.inp files to optimize the proton in Gaussian from the dummy .xyz files

### yzhou: load py3-numpy module to run python3
module load py3-numpy

if [ "$DEBUG" = true ]; then
echo $res
echo $default_NProcShared
echo "$calc_method"
fi

python3 $SCRIPT_DIR/scripts/proton_opt.py $res $default_NProcShared "$calc_method"
echo "[$(date +"%Y-%m-%d %T")] Proton optimization files created."


cd $dir/input/$res
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
python3 $SCRIPT_DIR/scripts/input_gen.py $res $default_NProcShared "$calc_method"
echo "[$(date +"%Y-%m-%d %T")] Gaussian input files created."


cd $dir/input/$res
# Run the .inp files in Gaussian to get .out files
for file in "${INPUT_NAMES[@]}"; do
    g16 < "$file.inp" > "$file.out" || echo "[$(date +"%Y-%m-%d %T")] $file energy calculation failed."
    echo "[$(date +"%Y-%m-%d %T")] $file Gaussian run done."
done

cd $dir
mkdir -p output/$res
# Calculates the strain and creates .tcl files to be visualized in VMD
python3 $SCRIPT_DIR/scripts/StrainViz.py $res
cp $dir/input/$res.xyz $dir/output/$res
echo "[$(date +"%Y-%m-%d %T")] StrainViz analysis finished."
