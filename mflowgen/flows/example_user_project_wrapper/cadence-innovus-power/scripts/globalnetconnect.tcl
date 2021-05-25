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


if { [ lindex [dbGet top.insts.cell.pgterms.name VPWR] 0 ] != 0x0 } {
  globalNetConnect vccd1 -type pgpin -pin VPWR -inst * -verbose
}

if { [ lindex [dbGet top.insts.cell.pgterms.name VGND] 0 ] != 0x0 } {
  globalNetConnect vssd1 -type pgpin -pin VGND -inst * -verbose
}


# Connect VNB / VPB if any cells have these pins
# TODO: Not sure about this! VNB and VPB are actually pwell and nwell connections!!

#if { [ lindex [dbGet top.insts.cell.pgterms.name VNB] 0 ] != 0x0 } {
#  globalNetConnect VSS -type pgpin -pin VNB -inst * -verbose
#}

#if { [ lindex [dbGet top.insts.cell.pgterms.name VPB] 0 ] != 0x0 } {
#  globalNetConnect VDD -type pgpin -pin VPB -inst * -verbose
#}

