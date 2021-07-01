#=========================================================================
# main.tcl
#=========================================================================
# A power strategy for the efabless MWP caravell example user project to use
# as macro with openlane
#
# Author : Maximilian Koschay
# Date   : 18.05.2021

# The openLane Flow does route power metal stripes across the macro
# Therefore the macro itself does not require a power ring and is not allowed
# to use the top metal layer
# here only the horizontal followpins need to be generated


#-------------------------------------------------------------------------
# Stdcell power rail preroute
#-------------------------------------------------------------------------
# Generate horizontal stdcell preroutes
sroute  -nets {vccd1 vssd1} 


#-------------------------------------------------------------------------
# Power mesh top settings (vertical)
#-------------------------------------------------------------------------
# Met 4 is highest allowed metal
# -> vertical stripes = met4 = "ADK_POWER_MESH_TOP_LAYER"
# -> horizontal stripes = met3 inside macro = "ADK_POWER_MESH_BOT_LAYER"
# -> but openlane creates horizontal stripes across macros on met5, thus
# horizontal power stripes inside macros should not be needed

if {[info exists ADK_BASE_LAYER_IDX]} {
  set base_layer_idx $ADK_BASE_LAYER_IDX
} else {
  set base_layer_idx 0
}

set pmesh_top $ADK_POWER_MESH_TOP_LAYER


set pmesh_min_width    [dbGet [dbGetLayerByZ $pmesh_top].minWidth]
set pmesh_route_pitchX [dbGet [dbGetLayerByZ $pmesh_top].pitchX]

# Bottom stripe params

set pmesh_top_str_width [expr  2 * $pmesh_min_width   ]
set pmesh_top_str_pitch [expr 10 * $pmesh_route_pitchX]

set pmesh_top_str_intraset_spacing [expr $pmesh_top_str_pitch - $pmesh_top_str_width]
set pmesh_top_str_interset_pitch   [expr 2*$pmesh_top_str_pitch]

setViaGenMode -reset
setViaGenMode -viarule_preference default
setViaGenMode -ignore_DRC false

setAddStripeMode -reset
setAddStripeMode -stacked_via_bottom_layer [expr $base_layer_idx + 1] \
                 -stacked_via_top_layer    $pmesh_top \
                 -break_at block_ring


# Add the stripes
addStripe -nets {vssd1 vccd1} -layer $pmesh_top -direction vertical \
    -width $pmesh_top_str_width                                 \
    -spacing $pmesh_top_str_intraset_spacing                    \
    -set_to_set_distance $pmesh_top_str_interset_pitch          \
    -max_same_layer_jog_length $pmesh_top_str_pitch             