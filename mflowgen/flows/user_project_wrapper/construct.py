#=========================================================================
# construct.py for the caravel user project wrapper together with the
# example user project (flat implementation!)
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

# Author : Maximilian Koschay
# Date   : 07.05.2021

import os

from mflowgen.components import Graph, Step

def construct():

  g = Graph()

  #-----------------------------------------------------------------------
  # Parameters
  #-----------------------------------------------------------------------
  # Define parameters that override the default parameters from the steps

  # Don't use topographical mode, as long as TLU+ files are missing
  # Skip Innovus connectivity verification since the design is quite large
  # which can result in memory overflow
  parameters = {
    'construct_path' : __file__,
    'design_name'    : 'user_project_wrapper',
    'topographical'  : False,
    'saif_instance'  : '',
    'clock_period'   : 10.0,
    'skip_verify_connectivity:' False
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

  #-----------------------------------------------------------------------
  # Get some default steps from the mflowgen repository
  #-----------------------------------------------------------------------
  
  # Synthesis step using Synopsys DC
  dc             = Step( 'synopsys-dc-synthesis',                   default=True )
  
  # PnR steps using Cadence Innovus
  iflow          = Step( 'cadence-innovus-flowsetup',               default=True )
  init           = Step( 'cadence-innovus-init',                    default=True )
  place          = Step( 'cadence-innovus-place',                   default=True )
  cts            = Step( 'cadence-innovus-cts',                     default=True )
  postcts_hold   = Step( 'cadence-innovus-postcts_hold',            default=True )
  route          = Step( 'cadence-innovus-route',                   default=True )
  postroute      = Step( 'cadence-innovus-postroute',               default=True )
  postroute_hold = Step( 'cadence-innovus-postroute_hold',          default=True )
  

  #-----------------------------------------------------------------------
  # Custom nodes from this repository
  #-----------------------------------------------------------------------

  # Signoff steps:

   # Custom Innovus signoff to flatten netlists for LVS netlist export
  signoff         = Step( common_SKY130_steps + '/cadence-innovus-signoff')

  # Although the Signoff DRC and LVS checks are already included in the
  # mflowgen master branch, there are some special steps required for
  # the SKY130 process
  # Steps were copied and partly modified from 
  # https://code.stanford.edu/ee272/skywater-digital-flow/-/tree/master

  # DRC  
  magic_drc       = Step( common_SKY130_steps + '/open-magic-drc'        )
  # Antenna DRC
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
  power                   = Step ( this_dir + '/cadence-innovus-power'  )
   

  #-----------------------------------------------------------------------
  # Manipulate the default nodes
  #-----------------------------------------------------------------------
  
  # since the initial floorplan including io locations and power rings is 
  # already given by the initial def file, the floorplan script and
  # io_placement step is skiped
  # if you want to place macros during the floorplan step, define a new 
  # floorplan.tcl script and give it the init step as input
  init_order = caravel_upr_floorplan.get_param('iInit_order')
  init.update_params({'order' : init_order})

  # Add setup.tcl to inputs of iflow step and initial .def file to inputs of init step
  iflow.extend_inputs(['setup.tcl'])
  iflow.extend_inputs(['user_project_wrapper.def'])
  init.extend_inputs(['user_project_wrapper.def', 'floorplan.tcl'])

  
  #-----------------------------------------------------------------------
  # Graph -- Add nodes
  #-----------------------------------------------------------------------

  g.add_step( rtl                     )
  g.add_step( constraints             )
  g.add_step( dc                      )
  g.add_step( wrapper_init_floorplan  )
  g.add_step( caravel_upr_floorplan   )
  g.add_step( iflow                   )
  g.add_step( init                    )
  g.add_step( power                   )
  g.add_step( place                   )
  g.add_step( cts                     )
  g.add_step( postcts_hold            )
  g.add_step( route                   )
  g.add_step( postroute               )
  g.add_step( postroute_hold          )
  g.add_step( signoff                 )
  g.add_step( magic_drc               )
  g.add_step( magic_antenna           )
  g.add_step( magic_gds2spice         )
  g.add_step( netgen_lvs_gds          )
  g.add_step( export_result           )

  #-----------------------------------------------------------------------
  # Graph -- Add edges
  #-----------------------------------------------------------------------

  # Connect by name

  g.connect_by_name( adk,            dc             )
  g.connect_by_name( adk,            iflow          )
  g.connect_by_name( adk,            init           )
  g.connect_by_name( adk,            power          )
  g.connect_by_name( adk,            place          )
  g.connect_by_name( adk,            cts            )
  g.connect_by_name( adk,            postcts_hold   )
  g.connect_by_name( adk,            route          )
  g.connect_by_name( adk,            postroute      )
  g.connect_by_name( adk,            postroute_hold )
  g.connect_by_name( adk,            signoff        )
  
  g.connect_by_name( adk,            magic_drc      )
  g.connect_by_name( adk,            magic_antenna  )

  g.connect_by_name( adk,            magic_gds2spice)
  g.connect_by_name( adk,            netgen_lvs_gds )

  g.connect_by_name( rtl,            dc             )
  g.connect_by_name( constraints,    dc             )

  g.connect_by_name( dc,             iflow          )
  g.connect_by_name( dc,             init           )
  g.connect_by_name( dc,             power          )
  g.connect_by_name( dc,             place          )
  g.connect_by_name( dc,             cts            )
  
  g.connect_by_name( wrapper_init_floorplan, iflow  )
  g.connect_by_name( wrapper_init_floorplan, init   )
  g.connect_by_name( caravel_upr_floorplan, iflow   )
  g.connect_by_name( caravel_upr_floorplan, init    )
    
  g.connect_by_name( iflow,          init           )
  g.connect_by_name( iflow,          power          )
  g.connect_by_name( iflow,          place          )
  g.connect_by_name( iflow,          cts            )
  g.connect_by_name( iflow,          postcts_hold   )
  g.connect_by_name( iflow,          route          )
  g.connect_by_name( iflow,          postroute      )
  g.connect_by_name( iflow,          postroute_hold )
  g.connect_by_name( iflow,          signoff        )

  g.connect_by_name( init,           power          )
  g.connect_by_name( power,          place          )
  g.connect_by_name( place,          cts            )
  g.connect_by_name( cts,            postcts_hold   )
  g.connect_by_name( postcts_hold,   route          )
  g.connect_by_name( route,          postroute      )
  g.connect_by_name( postroute,      postroute_hold )
  g.connect_by_name( postroute_hold, signoff        )

  g.connect_by_name( signoff,         magic_drc     )
  g.connect_by_name( signoff,         magic_antenna )


  g.connect_by_name( signoff,         magic_gds2spice )
  g.connect_by_name( signoff,         netgen_lvs_gds  )
  g.connect_by_name( magic_gds2spice, netgen_lvs_gds  )

  

  g.connect_by_name( signoff,         export_result   )
  g.connect_by_name( magic_gds2spice, export_result   )

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

