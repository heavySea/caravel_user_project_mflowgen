#! bin/bash
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
gunzip -c inputs/design.def.gz > $rep_root/def/user_project_wrapper.def

# 2. Copy the unmerge .gds
cp inputs/design.gds.gz $rep_root/gds/user_project_wrapper.gds.gz

# 3. Copy the LEF file
cp inputs/design.lef $rep_root/lef/user_project_wrapper.lef

# 3. Copy the spice model
cp inputs/design.lvs.spice $rep_root/spi/lvs/user_project_wrapper.spice

# 4. Copy the verilog gate-level netlist include pg terms