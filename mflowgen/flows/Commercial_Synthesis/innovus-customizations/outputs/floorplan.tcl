#=========================================================================
# floorplan.tcl
#=========================================================================
# Author : Maximilian Koschay
# Date   : 14.05.2021
#
# Basic floorplan and IO assignment for the user project area of the
# efabless caravel

# get core power net names from vars
set pwr_net_vdd [lindex [split $vars(power_nets) " "] 0]
set pwr_net_gnd [lindex [split $vars(ground_nets) " "] 0]

set pwr_net_list { ${pwr_net_vdd} ${pwr_net_gnd} }; # List of power nets in the core power ring

set M1_min_width   [dbGet [dbGetLayerByZ 1].minWidth]
set M1_min_spacing [dbGet [dbGetLayerByZ 1].minSpacing]

set savedvars(p_ring_width)   [expr 20 * $M1_min_width];   # Arbitrary!
set savedvars(p_ring_spacing) [expr 10 * $M1_min_spacing]; # Arbitrary!
 
 
#-------------------------------------------------------------------------
# Floorplan variables
#-------------------------------------------------------------------------

# The size of the user area is fixed to 2.92mm x 3.52mm and cannot be changed

