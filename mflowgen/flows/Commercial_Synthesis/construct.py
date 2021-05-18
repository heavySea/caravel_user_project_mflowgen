#=========================================================================
# construct.py
#=========================================================================
# ASIC flow using commercial EDA tools:
# Synopsys DC for synthesis
# Cadence Innovus for Place and Route
# Mentor Modelsim for Simulation (Replaceable with VCS)
# Synopsys PrimeTime (+ PX / Power Compiler) for Timing Sign-Off
# Magic for DRC 
# LVS with netgen
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

  power_estimation = True

  parameters = {
    'construct_path' : __file__,
    'design_name'    : 'user_project_wrapper',
    'topographical'  : True,
    'saif_instance'  : '',
    'clock_period'   : 10.0 
  }

  adk_parameters = {
    'adk'            : 'skywater-130nm',
    'adk_view'       : 'view-standard'
  }

  #-----------------------------------------------------------------------
  # Create nodes
  #-----------------------------------------------------------------------

  this_dir = os.path.dirname( os.path.abspath( __file__ ) )

  #-----------------------------------------------------------------------
  # ADK node
  #-----------------------------------------------------------------------

  g.set_adk( adk_parameters["adk"] )
  adk = g.get_adk_step()

  #-----------------------------------------------------------------------
  # Design node
  #-----------------------------------------------------------------------

  rtl            = Step( this_dir + '/design-rtl' )
  constraints    = Step( this_dir + '/design-constraints')

  #-----------------------------------------------------------------------
  # Default nodes
  #-----------------------------------------------------------------------

  dc             = Step( 'synopsys-dc-synthesis',                   default=True )
  iflow          = Step( 'cadence-innovus-flowsetup',       				default=True )
  init           = Step( 'cadence-innovus-init',                    default=True )
  place          = Step( 'cadence-innovus-place',                   default=True )
  cts            = Step( 'cadence-innovus-cts',                     default=True )
  postcts_hold   = Step( 'cadence-innovus-postcts_hold',            default=True )
  route          = Step( 'cadence-innovus-route',                   default=True )
  postroute      = Step( 'cadence-innovus-postroute',               default=True )
  postroute_hold = Step( 'cadence-innovus-postroute_hold',          default=True )
  signoff        = Step( 'cadence-innovus-signoff',                 default=True )

    
  #-----------------------------------------------------------------------
  # Custom nodes
  #-----------------------------------------------------------------------
  
  caravel_upr_floorplan   = Step ( this_dir + '/caravel-uprj-floorplan' )
  power                   = Step ( this_dir + '/cadence-innovus-power'  )

  #-----------------------------------------------------------------------
  # Manipulate nodes
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
  init.extend_inputs(['user_project_wrapper.def'])

	
  #-----------------------------------------------------------------------
  # Graph -- Add nodes
  #-----------------------------------------------------------------------

  g.add_step( rtl            )
  g.add_step( constraints    )
  g.add_step( dc             )
  g.add_step( caravel_upr_floorplan)
  g.add_step( iflow          )
  g.add_step( init           )
  g.add_step( power          )
  g.add_step( place          )
  g.add_step( cts            )
  g.add_step( postcts_hold   )
  g.add_step( route          )
  g.add_step( postroute      )
  g.add_step( postroute_hold )
  g.add_step( signoff        )

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

  g.connect_by_name( rtl,            dc             )
  g.connect_by_name( constraints,    dc             )

  g.connect_by_name( dc,             iflow          )
  g.connect_by_name( dc,             init           )
  g.connect_by_name( dc,             power          )
  g.connect_by_name( dc,             place          )
  g.connect_by_name( dc,             cts            )
	
  g.connect_by_name( caravel_upr_floorplan, iflow         )
  g.connect_by_name( caravel_upr_floorplan, init         )
  	
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


  #-----------------------------------------------------------------------
  # Parameterize
  #-----------------------------------------------------------------------
  
  g.update_params( adk_parameters )
  g.update_params( parameters )

  return g


if __name__ == '__main__':
  g = construct()
#  g.plot()

