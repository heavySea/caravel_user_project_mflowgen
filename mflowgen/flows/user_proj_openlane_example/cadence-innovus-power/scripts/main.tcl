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
