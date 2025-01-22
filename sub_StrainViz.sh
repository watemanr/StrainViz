#!/bin/bash

# 默认值
num_procs=48  # 默认核数
queue_name="standard"  # 默认队列名
method=""  # 默认计算方法为空
molecule=""  # 分子名字，必填

username=`whoami`
StrainViz_path="/home/$username/Apps/StrainViz"

# 打印帮助信息的函数
function print_help() {
  echo "Usage: $0 -r <molecule_name> [-N <num_procs>] [-q <queue_name>] [-m <method>] [-h]"
  echo ""
  echo "Options:"
  echo "  -r <molecule_name>   Specify the molecule name (required)"
  echo "  -N <num_procs>       Number of processors (default: 48)"
  echo "  -q <queue_name>      Queue name for job submission (default: standard)"
  echo "  -m <method>          Calculation method (optional)"
  echo "  -h                   Show this help message and exit"
  exit 0
}

# 解析命令行参数
while getopts "r:N:q:m:h" opt; do
  case $opt in
    r) molecule="$OPTARG" ;;  # 设置分子名字
    N) num_procs="$OPTARG" ;;  # 设置核数
    q) queue_name="$OPTARG" ;;  # 设置队列名
    m) method="$OPTARG" ;;  # 设置计算方法
    h) print_help ;;  # 显示帮助信息
    *) echo "Invalid option: -$OPTARG"; print_help ;;  # 处理无效参数
  esac
done

# 检查必填参数 -r 是否提供
if [[ -z "$molecule" ]]; then
  echo "Error: -r <molecule_name> is required."
  print_help
fi

# 输出参数值（调试用）
echo "StrainViz path: $StrainViz_path"
if [[ -f "$StrainViz_path/StrainViz-param.bash" ]]; then
  echo "StrainViz-param.bash exists in the directory: $StrainViz_path"
else
  echo "Error: StrainViz-param.bash does not exist in the directory: $StrainViz_path"
  exit 1
fi

echo "Molecule name: $molecule"
echo "Number of processors: $num_procs"
echo "Queue name: $queue_name"
if [[ -n "$method" ]]; then
  echo "Calculation method: $method"
else
  echo "Calculation method: None (optional)"
fi

JobName="StV_$molecule"

cat>sub_StrainViz_$molecule.slurm<<EOF
#!/bin/sh
#SBATCH -N 1 
#SBATCH -J $JobName
#SBATCH -n $num_procs
#SBATCH -p $queue_name 
#SBATCH -o $JobName-%j.out
#SBATCH -e $JobName-%j.err

dir=\`pwd\`
cd \$dir

EOF

if [[ -n "$method" ]]; then
echo "Calculation method: $method"
cat>>sub_StrainViz_$molecule.slurm<<EOF
bash StrainViz-param.bash -r $molecule -N $num_procs -m $method
EOF

else
cat>>sub_StrainViz_$molecule.slurm<<EOF
bash $StrainViz_path/StrainViz-param.bash -r $molecule -N $num_procs
EOF
fi

sbatch sub_StrainViz_$molecule.slurm

sleep 1