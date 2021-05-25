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
gunzip -c inputs/design.def.gz > $rep_root/def/user_project_wrapper.def || echo "WARNING: Could not copy design.def.gz! File not found?"

# 2. Copy the unmerge .gds
cp inputs/design.gds.gz $rep_root/gds/user_project_wrapper.gds.gz || echo "WARNING: Could not copy design.gds.gz! File not found?"

# 3. Copy the LEF file
cp inputs/design.lef $rep_root/lef/user_project_wrapper.lef || echo "WARNING: Could not copy design.lef! File not found?"

# 3. Copy the spice model
cp inputs/design.lvs.spice $rep_root/spi/lvs/user_project_wrapper.spice || echo "WARNING: Could not copy design.lvs.spice! File not found?"

# 4. Copy the verilog gate-level netlist include pg terms
cp inputs/design.vcs.pg.v $rep_root/verilog/gl/user_project_wrapper.v || echo "WARNING: Could not copy design.vcs.pg.v! File not found?"
# The Innovus generated netlist contains all pg stripe input reference, such as:
# .\vssa2.hori_r19 (vssa2), -> which is then used to assign the value of the power nets
# assign vssa2 = \vssa2.hori_r19 ;
# the MWP precheck looks for valid port declarations, so this might get a problem

# 5. .mag und .maglef files?