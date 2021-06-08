#=========================================================================
# pin-assignments.tcl
#=========================================================================
# Pin assignments for caravel example user project
# Author : Maximilian Koschay
# Date   : 09.06.2021

#-------------------------------------------------------------------------
# Pin Assignments
#-------------------------------------------------------------------------

# Use similar pin laytout as in openlane flow

set io_ports       [dbGet top.terms.name io_*]
set wb_ports       [dbGet top.terms.name wb*]
set la_ports       [dbGet top.terms.name la*]
set irq_ports      [dbGet top.terms.name irq*]


# Spread the pins evenly across the left and right sides of the block
set ports_layer met2

# not enough space for la ports all on one side

set num_la_ports        [llength $la_ports]
set half_la_ports_idx    [expr $num_la_ports / 2]

set la_pins_half_left   [lrange $la_ports 0 [expr $half_la_ports_idx - 4]]
set la_pins_half_bottom   [lrange $la_ports $half_la_ports_idx-3 [expr $num_la_ports - 1]]


for {set i 0} {$i < [llength $irq_ports]} {incr i} {
  lappend la_pins_half_left [lindex $irq_ports $i]
}


# use start and end offset to assure met2 min distance

set offset 0.625

# North: IO Pins
editPin -layer $ports_layer -pin $io_ports \
        -edge 3   -spreadType EDGE -offsetStart $offset -offsetEnd $offset 
# South: LA Ports
editPin -layer $ports_layer -pin $la_pins_half_bottom \
        -edge 1   -spreadType EDGE -offsetStart $offset -offsetEnd $offset 
# East: WB Pins
editPin -layer $ports_layer -pin $wb_ports \
        -edge 2   -spreadType EDGE -offsetStart $offset -offsetEnd $offset 
# West: IRQ
editPin -layer $ports_layer -pin $la_pins_half_left \
        -edge 0   -spreadType EDGE -offsetStart $offset -offsetEnd $offset 
