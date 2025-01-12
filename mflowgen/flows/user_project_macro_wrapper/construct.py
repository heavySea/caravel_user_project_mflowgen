#=========================================================================
# construct.py for the caravel user project wrapper without standard cells
#=========================================================================
# ASIC flow using commercial EDA tools:
# - Synopsys DC for synthesis
# - Cadence Innovus for Place and Route
# - (Mentor Modelsim for Simulation) (TODO)
# - (Synopsys PrimeTime (+ PX / Power Compiler) for Timing Sign-Off) (TODO)
# - Magic for DRC and Antenna Checks 
# - LVS with netgen
#
# This is excepted to be build from the Makefile in the root of the
# caravel user project repository
# Otherwise export following enviroment variables:
#
# export MFLOWGEN_PATH=/path/to/SKY130_ADK_Repository
#
# Wrapper implementation flow that uses the previous build 
# user_proj_example macro! 

# Author : Maximilian Koschay
# Date   : 11.06.2021

import os

from mflowgen.components import Graph, Step

# The PnR steps are packed into an python dictionary
# Here are some handy helper functions defined to add all steps
# to the graph and connect all the steps to a given other step

def add_step_set_to_graph(graph, step_dict):
  for step in step_dict.values():
    graph.add_step(step)
    

def connect_ports_to_step_set(graph, output_step, input_dict):
  for step in input_dict.values():
    if output_step.get_name()!=step.get_name():
      graph.connect_by_name(output_step, step)

# The actuall flow specification follows here:

def construct():

  g = Graph()

  #-----------------------------------------------------------------------
  # Parameters
  #-----------------------------------------------------------------------
  # Define parameters that override the default parameters from the steps

  # Don't use topographical mode, as long as TLU+ files are missing
  parameters = {
    'construct_path' : __file__,
    'design_name'    : 'user_project_wrapper',
    'topographical'  : False,
    'saif_instance'  : '',
    'clock_period'   : 10.0,
    'add_fillers'    : False
  }

  adk_parameters = {
    'adk'            : 'skywater-130nm',
    'adk_view'       : 'view-standard'
  }

  #-----------------------------------------------------------------------
  # Define some source directories
  #-----------------------------------------------------------------------

  this_dir            = os.path.dirname( os.path.abspath( __file__ ) )
  common_SKY130_steps = os.path.dirname( os.path.abspath( __file__ ) ) + '/../../common_mflowgen_steps'
  # Using an enviroment variable would be better:
  #common_SKY130_steps = os.env('MFLOWGEN_STEP_PATH')

  #-----------------------------------------------------------------------
  # Set the ADK node
  #-----------------------------------------------------------------------

  g.set_adk( adk_parameters["adk"] )
  adk = g.get_adk_step()

  #-----------------------------------------------------------------------
  # Get some design specific steps
  #-----------------------------------------------------------------------

  rtl            = Step( this_dir + '/design-rtl'        )
  constraints    = Step( this_dir + '/design-constraints')
  example_macro  = Step( this_dir + '/example-macro')

  #-----------------------------------------------------------------------
  # Get some default steps from the mflowgen repository
  #-----------------------------------------------------------------------

  # Synthesis step using Synopsys DC
  dc             = Step( 'synopsys-dc-synthesis',                   default=True )

  # PnR steps using Cadence Innovus
  # To make adding nodes repeatedly a litte bit easier, pack all the innovus step
  # in a dictionary
  pnr_steps = {
    "iflow"           : Step( 'cadence-innovus-flowsetup',               default=True ),
    "init"            : Step( 'cadence-innovus-init',                    default=True ),
    "place"           : Step( 'cadence-innovus-place',                   default=True ),
    "cts"             : Step( 'cadence-innovus-cts',                     default=True ),
    "postcts_hold"    : Step( 'cadence-innovus-postcts_hold',            default=True ),
    "route"           : Step( 'cadence-innovus-route',                   default=True ),
    "postroute"       : Step( 'cadence-innovus-postroute',               default=True ),
    "postroute_hold"  : Step( 'cadence-innovus-postroute_hold',          default=True )
  }
  

  #-----------------------------------------------------------------------
  # Custom nodes from this repository
  #-----------------------------------------------------------------------

  # Signoff steps:

  # Custom Innovus signoff to flatten netlists for LVS netlist export
  pnr_steps["signoff"]    = Step( common_SKY130_steps + '/cadence-innovus-signoff')

  # Although the Signoff DRC and LVS checks are already included in the
  # mflowgen master branch, there are some special steps required for
  # the SKY130 process
  # Steps were copied and partly modified from 
  # https://code.stanford.edu/ee272/skywater-digital-flow/-/tree/master

  # DRC  
  magic_drc       = Step( common_SKY130_steps + '/open-magic-drc'        )
  # Antenna checks
  magic_antenna   = Step( common_SKY130_steps + '/open-magic-antenna'        )

  # LVS can either use GDS or DEF as source for spice generation
  # Use only merged GDS extraction for now (DEF extraction failes)
  # magic_def2spice = Step( common_SKY130_steps + '/open-magic-def2spice'   )
  magic_gds2spice = Step( common_SKY130_steps + '/open-magic-gds2spice'   )
  
  netgen_lvs_gds  = Step( common_SKY130_steps + '/open-netgen-lvs'        )
  # netgen_lvs_def  = netgen_lvs_def.clone()
  netgen_lvs_gds.set_name('netgen-lvs-gds')
  # netgen_lvs_def.set_name('netgen-lvs-def')

  # Export:  

  # Export the results to the MWP caravel directory strucutures
  export_result   = Step( common_SKY130_steps + '/caravel-uprj-export'    )

  #-----------------------------------------------------------------------
  # Custom nodes for this specific design
  #-----------------------------------------------------------------------
  
  # The outline and pin positions of the wrapper must be exactly as defined
  # by the caravel 
  # Use an edited DEF file as initial floorplan
  wrapper_init_floorplan  = Step( common_SKY130_steps + '/caravel-wrapper-init-fp')


  # Add steps that provide modifications for the floorplan and power steps 
  # for the PnR flow
  caravel_upr_floorplan   = Step ( this_dir + '/caravel-uprj-floorplan' )
  pnr_steps["power"]      = Step ( this_dir + '/cadence-innovus-power'  )
   

  #-----------------------------------------------------------------------
  # Manipulate the default nodes
  #-----------------------------------------------------------------------
  
  # Add the example project macro timing library to the synthesis step
  dc.extend_inputs(['user_proj_example_TT.db'])
  # Remove DC clock gating post-condition, since there are not stdcells to
  # be power-gated
  dc.set_postconditions(dc.get_postconditions()[:-1])


  # since the initial floorplan including io locations and power rings is 
  # already given by the initial def file, the floorplan script and
  # io_placement step is skiped
  # if you want to place macros during the floorplan step, define a new 
  # floorplan.tcl script and give it the init step as input
  init_order = caravel_upr_floorplan.get_param('iInit_order')
  pnr_steps["init"].update_params({'order' : init_order})

  # Add setup.tcl to inputs of iflow step and initial .def file to inputs of init step
  pnr_steps["iflow"].extend_inputs(['setup.tcl'])
  pnr_steps["iflow"].extend_inputs(['user_project_wrapper.def'])
  pnr_steps["init"].extend_inputs(['user_project_wrapper.def', 'floorplan.tcl'])

  # Add the example project macro GDS for final GDS merging
  pnr_steps["signoff"].extend_inputs(['user_proj_example.gds.gz'])

  # Add macro lef and timing lib to pnr steps
  for pnr_s in pnr_steps.values(): 
    pnr_s.extend_inputs(['user_proj_example.lef', 'user_proj_example_TT.lib'])
  

  #-----------------------------------------------------------------------
  # Graph -- Add nodes
  #-----------------------------------------------------------------------

  g.add_step( rtl                         )
  g.add_step( constraints                 )
  g.add_step( example_macro               )
  g.add_step( dc                          )
  g.add_step( wrapper_init_floorplan      )
  g.add_step( caravel_upr_floorplan       )
  add_step_set_to_graph( g, pnr_steps     )

  g.add_step( magic_drc                   )
  g.add_step( magic_antenna               )
  g.add_step( magic_gds2spice             )
  g.add_step( netgen_lvs_gds              )

  g.add_step( export_result               )

  #-----------------------------------------------------------------------
  # Graph -- Add edges
  #-----------------------------------------------------------------------

  # Connect by name

  g.connect_by_name( adk,            dc                                       )
  connect_ports_to_step_set( g, adk, pnr_steps                                )
  g.connect_by_name( adk,            magic_drc                                )
  g.connect_by_name( adk,            magic_antenna                            )
  g.connect_by_name( adk,            magic_gds2spice                          )
  g.connect_by_name( adk,            netgen_lvs_gds                           )

  g.connect_by_name( rtl,            dc                                       )
  g.connect_by_name( constraints,    dc                                       )

  g.connect_by_name( dc,             pnr_steps["iflow"]                       )
  g.connect_by_name( dc,             pnr_steps["init"]                        )
  g.connect_by_name( dc,             pnr_steps["power"]                       )
  g.connect_by_name( dc,             pnr_steps["place"]                       )
  g.connect_by_name( dc,             pnr_steps["cts"]                         )

  g.connect_by_name( wrapper_init_floorplan, pnr_steps["iflow"]               )
  g.connect_by_name( wrapper_init_floorplan, pnr_steps["init"]                )
  g.connect_by_name( caravel_upr_floorplan, pnr_steps["iflow"]                )
  g.connect_by_name( caravel_upr_floorplan, pnr_steps["init"]                 )

  g.connect_by_name( example_macro,  dc                                       )
  connect_ports_to_step_set( g, example_macro, pnr_steps                      )
  
  connect_ports_to_step_set( g, pnr_steps["iflow"], pnr_steps                 )

  g.connect_by_name( pnr_steps["init"],           pnr_steps["power"]          )
  g.connect_by_name( pnr_steps["power"],          pnr_steps["place"]          )
  g.connect_by_name( pnr_steps["place"],          pnr_steps["cts"]            )
  g.connect_by_name( pnr_steps["cts"],            pnr_steps["postcts_hold"]   )
  g.connect_by_name( pnr_steps["postcts_hold"],   pnr_steps["route"]          )
  g.connect_by_name( pnr_steps["route"],          pnr_steps["postroute"]      )
  g.connect_by_name( pnr_steps["postroute"],      pnr_steps["postroute_hold"] )
  g.connect_by_name( pnr_steps["postroute_hold"], pnr_steps["signoff"]        )

  g.connect_by_name( pnr_steps["signoff"],         magic_drc                  )
  g.connect_by_name( pnr_steps["signoff"],         magic_antenna              )

  g.connect_by_name( pnr_steps["signoff"],         magic_gds2spice            )
  g.connect_by_name( pnr_steps["signoff"],         netgen_lvs_gds             )
  g.connect_by_name( magic_gds2spice, netgen_lvs_gds                          )

  

  g.connect_by_name( pnr_steps["signoff"],         export_result              )
  g.connect_by_name( magic_gds2spice, export_result                           )

  #-----------------------------------------------------------------------
  # Parameterize
  #-----------------------------------------------------------------------
  # Apply the above defined parameters to all stepgs in the graph

  g.update_params( adk_parameters )
  g.update_params( parameters )

  return g


if __name__ == '__main__':
  g = construct()
#  g.plot()

