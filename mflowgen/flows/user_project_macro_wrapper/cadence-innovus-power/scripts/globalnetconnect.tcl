#=========================================================================
# globalnetconnect.tcl
#=========================================================================
# Author : Christopher Torng
# Date   : January 13, 2020
#
# Edited for SKY130 caravel project
# Author : Maximilian Koschay
# Date   : 18.05.2021


#-------------------------------------------------------------------------
# Global net connections for PG pins
#-------------------------------------------------------------------------

# Connect SKY130 pg pins with VCCD1/VSSD1
# This connects all cells and macros to one digitial pg net!
# Specify the -inst argument to select which instances to connect to which
# power domain if your design cointains multiple!

if { [ lindex [dbGet top.insts.cell.pgterms.name VPWR] 0 ] != 0x0 } {
  globalNetConnect vccd1 -type pgpin -pin VPWR -inst * -verbose
}

if { [ lindex [dbGet top.insts.cell.pgterms.name VGND] 0 ] != 0x0 } {
  globalNetConnect vssd1 -type pgpin -pin VGND -inst * -verbose
}


if { [ lindex [dbGet top.insts.cell.pgterms.name VNB] 0 ] != 0x0 } {
  globalNetConnect vssd1 -type pgpin -pin VNB -inst * -verbose
}

if { [ lindex [dbGet top.insts.cell.pgterms.name VPB] 0 ] != 0x0 } {
  globalNetConnect vccd1 -type pgpin -pin VPB -inst * -verbose
}

# Pin connections for the macro blocks

if { [ lindex [dbGet top.insts.cell.pgterms.name vccd1] 0 ] != 0x0 } {
  globalNetConnect vccd1 -type pgpin -pin vccd1 -inst * -verbose
}

if { [ lindex [dbGet top.insts.cell.pgterms.name vssd1] 0 ] != 0x0 } {
  globalNetConnect vssd1 -type pgpin -pin vssd1 -inst * -verbose
}
