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
# Placement density of 60% is reasonable for 4 useable metal layers
set core_density_target 0.6; 



#-------------------------------------------------------------------------
# Shorter names from the ADK
#-------------------------------------------------------------------------

if {[info exists ADK_BASE_LAYER_IDX]} {
  set met2_layer_idx [expr $ADK_BASE_LAYER_IDX + 1]
} else {
  set met2_layer_idx 2
}

#-------------------------------------------------------------------------
# Core <-> Boundary margin
#-------------------------------------------------------------------------
# the macro will not have a power ring therefore we do not need as much margin
# Neverheless leave some space for IO routing as there are a lot of IO ports

# get min width an spacing from met2 layer
set M2_min_width   [dbGet [dbGetLayerByZ $met2_layer_idx].minWidth]
set M2_min_spacing [dbGet [dbGetLayerByZ $met2_layer_idx].minSpacing]

# allow 20 met2 wires to be routed next to each other
# increase space and min widht a little bit, just to be safe

set core_margin   [expr (2 * $M2_min_spacing) + ( 20 * ($M2_min_width * 2 + $M2_min_spacing * 2))]

#-------------------------------------------------------------------------
# Floorplan
#-------------------------------------------------------------------------

# Calling floorPlan with the "-r" flag sizes the floorplan according to
# the core aspect ratio and a density target (70% is a reasonable
# density).
#

floorPlan -r $core_aspect_ratio $core_density_target \
             $core_margin $core_margin $core_margin $core_margin

setFlipping s

# Use automatic floorplan synthesis to pack macros (e.g., SRAMs) together

planDesign