# Place the macro close to the LA ports
create_relative_floorplan -ref_type core_boundary -horizontal_edge_separate {3  150  3} -vertical_edge_separate {0  1300  0} -place mprj
snapFPlan -block
# create placement blockage for easier pin routing
addHaloToBlock -snapToSite 10 10 10 10 mprj

setFlipping s



# set dont touch to all nets -> do not insert buffers on top level
set_dont_touch [get_nets *] true