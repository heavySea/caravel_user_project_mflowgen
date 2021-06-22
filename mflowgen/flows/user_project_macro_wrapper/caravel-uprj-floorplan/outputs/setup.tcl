# Sepcify the initial Floorplan DEF file
set vars(def_files)                  inputs/user_project_wrapper.def

# Correct the names of the power nets as used in the DEF file:
# VCCD1 and VSSD1 should be equivalent to digital VDD and GND at 1,8V
# VCCD2 and VSSD2 can be used as a second power suppy, e.g. for macros (not utilized in the example)
# VDDA1/VSSA1 and VDDA1/VSSA1 are 3.3V analog power/ground
set vars(power_nets)  "vccd1 vccd2 vdda1 vdda2"
set vars(ground_nets) "vssd1 vssd2 vssa1 vssa2"


# unset Filler Cell, since no device filling needed on chip level
# this will remove the insertion of filler cells

unset vars(filler_cells)

# unset Antenna cell to disable antenna fixing on top level cell
unset vars(antenna_diode)  

# Set don't use cells after the init step:
set vars(dont_use_list)               $ADK_DONT_USE_CELLS_OPT


# OCV (on-chip variation)

#set vars(enable_ocv)    pre_postroute
#set vars(enable_si_aware) false

