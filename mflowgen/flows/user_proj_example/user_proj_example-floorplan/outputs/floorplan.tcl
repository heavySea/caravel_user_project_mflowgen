#=========================================================================
# floorplan.tcl
#=========================================================================
# Author : Christopher Torng
# Date   : March 26, 2018
# 
# Modified for caravel example user project
# Author : Maximilian Koschay
# Date   : June 09, 2021

#-------------------------------------------------------------------------
# Floorplan variables
#-------------------------------------------------------------------------

# Set the floorplan to target a reasonable placement density with a good
# aspect ratio (height:width). An aspect ratio of 2.0 here will make a
# rectangular chip with a height that is twice the width.

set core_aspect_ratio   1.00; # Aspect ratio 1.0 for a square chip
set core_density_target 0.70; # Placement density of 70% is reasonable



#-------------------------------------------------------------------------
# Shorter names from the ADK
#-------------------------------------------------------------------------

if {[info exists ADK_POWER_MESH_TOP_LAYER]} {
  set top_layer_idx $ADK_POWER_MESH_TOP_LAYER
} else {
  set top_layer_idx 0
}

# Make room in the floorplan for the core power ring

# get core power net names from vars
# should return vccd1 and vssd1
set pwr_net_vdd [lindex [split $vars(power_nets) " "] 0]
set pwr_net_gnd [lindex [split $vars(ground_nets) " "] 0]

set pwr_net_list { ${pwr_net_vdd} ${pwr_net_gnd} }; # List of power nets in the core power ring

# get min width an spacing from top layer
set M5_min_width   [dbGet [dbGetLayerByZ $top_layer_idx].minWidth]
set M5_min_spacing [dbGet [dbGetLayerByZ $top_layer_idx].minSpacing]

set savedvars(p_ring_width)   [expr 5 * $M5_min_width];   # Arbitrary!
set savedvars(p_ring_spacing) [expr 5 * $M5_min_spacing]; # Arbitrary!

# Core bounding box margins

set core_margin_t [expr ([llength $pwr_net_list] * ($savedvars(p_ring_width) + $savedvars(p_ring_spacing))) + $savedvars(p_ring_spacing)]
set core_margin_b [expr ([llength $pwr_net_list] * ($savedvars(p_ring_width) + $savedvars(p_ring_spacing))) + $savedvars(p_ring_spacing)]
set core_margin_r [expr ([llength $pwr_net_list] * ($savedvars(p_ring_width) + $savedvars(p_ring_spacing))) + $savedvars(p_ring_spacing)]
set core_margin_l [expr ([llength $pwr_net_list] * ($savedvars(p_ring_width) + $savedvars(p_ring_spacing))) + $savedvars(p_ring_spacing)]

#-------------------------------------------------------------------------
# Floorplan
#-------------------------------------------------------------------------

# Calling floorPlan with the "-r" flag sizes the floorplan according to
# the core aspect ratio and a density target (70% is a reasonable
# density).
#

floorPlan -r $core_aspect_ratio $core_density_target \
             $core_margin_l $core_margin_b $core_margin_r $core_margin_t

setFlipping s

# Use automatic floorplan synthesis to pack macros (e.g., SRAMs) together

planDesign