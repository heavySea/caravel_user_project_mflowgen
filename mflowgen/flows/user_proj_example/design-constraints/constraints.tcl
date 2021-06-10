#=========================================================================
# Design Constraints File
#=========================================================================

set la_clock_net  la_data_in[64]
set la_clock_name la_clock

set wb_clock_net  wb_clk_i
set wb_clock_name ideal_wb_clock

create_clock -name ${la_clock_name} \
             -period ${dc_clock_period} \
             [get_ports ${la_clock_net}]

create_clock -name ${wb_clock_name} \
             -period ${dc_clock_period} \
             [get_ports ${wb_clock_net}]


set clock_ports [filter_collection \
                       [get_attribute [get_clocks] sources] \
                       object_class==port]

set signal_ports [remove_from_collection [all_inputs] ${clock_ports}]

# This constraint sets the load capacitance in picofarads of the
# output pins of your design.

set_load -pin_load $ADK_TYPICAL_ON_CHIP_LOAD [all_outputs]

# This constraint sets the input drive strength of the input pins of
# your design. We specify a specific standard cell which models what
# would be driving the inputs. This should usually be a small inverter
# which is reasonable if another block of on-chip logic is driving
# your inputs.

set_driving_cell -no_design_rule \
  -lib_cell $ADK_DRIVING_CELL [all_inputs]

# set_input_delay constraints for input ports
# Make this non-zero to avoid hold buffers on input-registered designs

set_input_delay -clock ${la_clock_name} [expr ${dc_clock_period}/3.0] ${signal_ports}
set_input_delay -clock ${wb_clock_name} [expr ${dc_clock_period}/3.0] ${signal_ports}

# set_output_delay constraints for output ports

set_output_delay -max -clock ${la_clock_name} 0.5 [all_outputs]
set_output_delay -max -clock ${wb_clock_name} 0.5 [all_outputs]


# set clock selection mux to only use sel=0 (wb_clock) during analysis ->
set_case_analysis 1    [ get_ports  la_oenb[64] ]
set_case_analysis 1    [ get_ports  la_oenb[65] ]


# asynchrone reset paths

set_false_path -from [get_ports wb_rst_i]

# Make all signals limit their fanout

set_max_fanout 20 $dc_design_name

# Make all signals meet good slew

#set_max_transition [expr 0.5*${dc_clock_period}] $dc_design_name

#set_input_transition 1 [all_inputs]
#set_max_transition 10 [all_outputs]

set_dont_use [get_lib_cells {*/*probec* }]

