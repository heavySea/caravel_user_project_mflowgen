#=========================================================================
# export results.sh
#=========================================================================
# This script exports the result of a run to the MWP caraval directories
#
# Author : Maximilian Koschay
# Date   : 20.05.2021

# set root directory
# assuming to be in a step of a build directory in repository_root/mflowgen
export rep_root=../../..

# 1. Copy final .def file from Innovus Signoff step and unpack ist
gunzip -c inputs/design.def.gz > $rep_root/def/${design_name}.def || echo "WARNING: Could not copy design.def.gz! File not found?"

# 2. Copy the unmerge .gds
cp inputs/design.gds.gz $rep_root/gds/${design_name}.gds.gz || echo "WARNING: Could not copy design.gds.gz! File not found?"

# 3. Copy the LEF file
cp inputs/design.lef $rep_root/lef/${design_name}.lef || echo "WARNING: Could not copy design.lef! File not found?"

# 3. Copy the spice model
cp inputs/design.lvs.spice $rep_root/spi/lvs/${design_name}.spice || echo "WARNING: Could not copy design.lvs.spice! File not found?"

# 4. Copy the verilog gate-level netlist include pg terms
cp inputs/design.vcs.pg.v $rep_root/verilog/gl/${design_name}.v || echo "WARNING: Could not copy design.vcs.pg.v! File not found?"
