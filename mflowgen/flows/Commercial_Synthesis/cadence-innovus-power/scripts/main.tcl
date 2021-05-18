#=========================================================================
# main.tcl
#=========================================================================
# A power strategy for the efabless MWP caravell user project wrapper 
#
# Author : Maximilian Koschay
# Date   : 18.05.2021

# The initial floorplan already provides power rings around the core area
# which must not be changed!
# the original pg stripes and cell connections over the core area have been
# removed to allow easier macro placement

# The example project is quite simple.
# It only uses one of the two available digital power supplies and no
# analog power supply. It does not contain any macro or special cells. 


#-------------------------------------------------------------------------
# Shorter names from the ADK
#-------------------------------------------------------------------------

if {[info exists ADK_BASE_LAYER_IDX]} {
  set base_layer_idx $ADK_BASE_LAYER_IDX
} else {
  set base_layer_idx 0
}

set pmesh_bot $ADK_POWER_MESH_BOT_LAYER
set pmesh_top $ADK_POWER_MESH_TOP_LAYER

#-------------------------------------------------------------------------
# Ring width calculation was skipped in the init step
#-------------------------------------------------------------------------

set M5_min_width   [dbGet [dbGetLayerByName met5].minWidth]
set M5_min_spacing [dbGet [dbGetLayerByZ met5].minSpacing]

set savedvars(p_ring_width)   [expr 20 * $M5_min_width];   # Arbitrary!
set savedvars(p_ring_spacing) [expr 24 * $M5_min_spacing]; # Arbitrary!

#-------------------------------------------------------------------------
# Macro Power rings
#-------------------------------------------------------------------------
# If you need to add rings accross macros do it here
#selectInst $macro
#addRing -nets {vccd1 vssd1} -type block_rings \
#        -around selected \
#        -layer [list top  $pmesh_top bottom $pmesh_top  \
#                     left $pmesh_bot right  $pmesh_bot] \
#        -width $savedvars(p_ring_width)                 \
#        -spacing $savedvars(p_ring_spacing)             \
#        -offset $savedvars(p_ring_spacing)    \
#        -extend_corner {lt rt tl bl }
#deselectAll


#-------------------------------------------------------------------------
# Power mesh bottom settings (vertical)
#-------------------------------------------------------------------------
# - pmesh_bot_str_width            : 8X thickness compared to 3 * M1 width
# - pmesh_bot_str_pitch            : Arbitrarily choosing the stripe pitch
# - pmesh_bot_str_intraset_spacing : Space between VSS/VDD, choosing
#                                    constant pitch across VSS/VDD stripes
# - pmesh_bot_str_interset_pitch   : Pitch between same-signal stripes

# Get M1 min width and signal routing pitch as defined in the LEF

set M1_min_width    [dbGet [dbGetLayerByZ [expr $base_layer_idx + 1]].minWidth]
set M1_route_pitchX [dbGet [dbGetLayerByZ [expr $base_layer_idx + 1]].pitchX]

# Bottom stripe params

set pmesh_bot_str_width [expr  8 *  3 * $M1_min_width   ]
set pmesh_bot_str_pitch [expr 4 * 10 * $M1_route_pitchX]

set pmesh_bot_str_intraset_spacing [expr $pmesh_bot_str_pitch - $pmesh_bot_str_width]
set pmesh_bot_str_interset_pitch   [expr 2*$pmesh_bot_str_pitch]

setViaGenMode -reset
setViaGenMode -viarule_preference default
setViaGenMode -ignore_DRC false

setAddStripeMode -reset
setAddStripeMode -stacked_via_bottom_layer [expr $base_layer_idx + 1] \
                 -stacked_via_top_layer    $pmesh_top \
                 -break_at block_ring \
                 -extend_to_closest_target stripe


# Add the stripes
#
# Use -start to offset the stripes slightly away from the core edge.
# Allow same-layer jogs to connect stripes to the core ring if some
# blockage is in the way (e.g., connections from core ring to pads).
# Restrict any routing around blockages to use only layers for power.

addStripe -nets {vssd1 vccd1} -layer $pmesh_bot -direction vertical \
    -width $pmesh_bot_str_width                                 \
    -spacing $pmesh_bot_str_intraset_spacing                    \
    -set_to_set_distance $pmesh_bot_str_interset_pitch          \
    -max_same_layer_jog_length $pmesh_bot_str_pitch             \
    -padcore_ring_bottom_layer_limit $pmesh_bot                 \
    -padcore_ring_top_layer_limit $pmesh_top                    \
    -start [expr $pmesh_bot_str_pitch]


#-------------------------------------------------------------------------
# Power mesh top settings (horizontal)
#-------------------------------------------------------------------------
# - pmesh_top_str_width            : 8X thickness compared to 3 * M1 width
# - pmesh_top_str_pitch            : Arbitrarily choosing the stripe pitch
# - pmesh_top_str_intraset_spacing : Space between VSS/VDD, choosing
#                                    constant pitch across VSS/VDD stripes
# - pmesh_top_str_interset_pitch   : Pitch between same-signal stripes

set pmesh_top_str_width [expr  8 *  3 * $M1_min_width   ]
set pmesh_top_str_pitch [expr 4 * 10 * $M1_route_pitchX]

set pmesh_top_str_intraset_spacing [expr $pmesh_top_str_pitch - $pmesh_top_str_width]
set pmesh_top_str_interset_pitch   [expr 2*$pmesh_top_str_pitch]

setViaGenMode -reset
setViaGenMode -viarule_preference default
setViaGenMode -ignore_DRC false

setAddStripeMode -reset
setAddStripeMode -stacked_via_bottom_layer $pmesh_bot \
                 -stacked_via_top_layer    $pmesh_top \
                 -break_at block_ring \
                 -extend_to_closest_target ring

# Add the stripes
#
# Use -start to offset the stripes slightly away from the core edge.
# Allow same-layer jogs to connect stripes to the core ring if some
# blockage is in the way (e.g., connections from core ring to pads).
# Restrict any routing around blockages to use only layers for power.

addStripe -nets {vssd1 vccd1} -layer $pmesh_top -direction horizontal \
    -width $pmesh_top_str_width                                   \
    -spacing $pmesh_top_str_intraset_spacing                      \
    -set_to_set_distance $pmesh_top_str_interset_pitch            \
    -max_same_layer_jog_length $pmesh_top_str_pitch               \
    -padcore_ring_bottom_layer_limit $pmesh_bot                   \
    -padcore_ring_top_layer_limit $pmesh_top                      \
    -start [expr $pmesh_top_str_pitch] \
    -extend_to first_padring

#-------------------------------------------------------------------------
# Stdcell power rail preroute
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
# Stdcell power rail preroute
#-------------------------------------------------------------------------
# Generate horizontal stdcell preroutes
sroute -nets {vccd1 vssd1} -connect { blockPin corePin floatingStripe}

