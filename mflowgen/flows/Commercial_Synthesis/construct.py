#=========================================================================
# construct.py
#=========================================================================
# ASIC flow using commercial EDA tools:
# Synopsys DC for synthesis
# Cadence Innovus for Place and Route
# Mentor Modelsim for Simulation (Replaceable with VCS)
# Synopsys PrimeTime (+ PX / Power Compiler) for Timing Sign-Off
# Magic for DRC (Replaceable with Calibre)
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
    'design_name'    : 'memory',
    'topographical'  : True,
    'saif_instance'  : 'testbench/scm_1r_1w_be_inst'
  }

  adk_parameters = {
    'adk'            : 'skywater-130nm',
    'adk_view'       : 'view-extended',
    'chip_level'     : False,
    'stdlibs'        : 'CORE65LPSVT,CORE65LPHVT,CORE65LPLVT',
    'link_stdlibs'   : '',
    'iolibs'         : '',
  }

  #-----------------------------------------------------------------------
  # Create nodes
  #-----------------------------------------------------------------------

  this_dir = os.path.dirname( os.path.abspath( __file__ ) )

  #-----------------------------------------------------------------------
  # ADK node
  #-----------------------------------------------------------------------

  g.set_adk( 'stm-65nm' )
  adk = g.get_adk_step()

  #-----------------------------------------------------------------------
  # Design node
  #-----------------------------------------------------------------------

  rtl            = Step( this_dir + '/rtl' )
  testbench      = Step( this_dir + '/testbench')
  constraints    = Step( this_dir + '/design-constraints')

  #-----------------------------------------------------------------------
  # Default nodes
  #-----------------------------------------------------------------------

  dc_cmos65      = Step( 'synopsys-dc-synthesis-cmos65-additions',  default=True )
  dc             = Step( 'synopsys-dc-synthesis',                   default=True )
  iflow          = Step( 'cadence-innovus-flowsetup-cmos056',       default=True )
  init           = Step( 'cadence-innovus-init',                    default=True )
  power          = Step( 'cadence-innovus-power-cmos056',           default=True )
  place          = Step( 'cadence-innovus-place',                   default=True )
  cts            = Step( 'cadence-innovus-cts',                     default=True )
  postcts_hold   = Step( 'cadence-innovus-postcts_hold',            default=True )
  route          = Step( 'cadence-innovus-route',                   default=True )
  postroute      = Step( 'cadence-innovus-postroute',               default=True )
  postroute_hold = Step( 'cadence-innovus-postroute_hold',          default=True )
  signoff        = Step( 'cadence-innovus-signoff',                 default=True )
  vcs_gl_sim     = Step( 'synopsys-vcs-sim',                        default=True )
  gl_power_est   = Step( 'synopsys-pt-power',                       default=True )
    
  #-----------------------------------------------------------------------
  # Custom nodes
  #-----------------------------------------------------------------------
  
  # custom_nide = Steo( ../../custom_steps/custom-step )

  #-----------------------------------------------------------------------
  # Manipulate nodes
  #-----------------------------------------------------------------------

  # Synopsys DC synthesis śTM ADK additions
  # The default DC node must be modified to support the STM65nm ADK
  dc.extend_inputs( dc_cmos65.all_outputs() )

  nom_lib_condition = adk.get_param('nom_conditions')
  dc_cmos65.update_params( {'nom_conditions' : nom_lib_condition} )
  dc.update_params( dc_cmos65.params(), allow_new=True )


  # Change Synopsys DC Step Inputs to enable multi-file designs
  # Extend the inputs... the read_design.tcl replaces the original script inside the step
  dc.extend_inputs( ["read-design.tcl", "rtl"] )


  # GL Power estimation
  vcs_gl_sim.update_params(testbench.params())
  gl_power_est.update_params( {'lib_op_condition' : nom_lib_condition})


  #-----------------------------------------------------------------------
  # Graph -- Add nodes
  #-----------------------------------------------------------------------

  g.add_step( rtl            )
  g.add_step( constraints    )
  g.add_step( dc_cmos65      )
  g.add_step( dc             )
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

  g.add_step( testbench      )
  g.add_step( vcs_gl_sim     )
  g.add_step( gl_power_est   )

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

  g.connect_by_name( dc_cmos65,      dc             )
  g.connect_by_name( rtl,            dc             )
  g.connect_by_name( constraints,    dc             )

  g.connect_by_name( dc,             iflow          )
  g.connect_by_name( dc,             init           )
  g.connect_by_name( dc,             power          )
  g.connect_by_name( dc,             place          )
  g.connect_by_name( dc,             cts            )

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

  g.connect_by_name( adk,             vcs_gl_sim     )
  g.connect_by_name( signoff,         vcs_gl_sim     )
  g.connect_by_name( testbench,       vcs_gl_sim     )
    
  g.connect_by_name( adk,             gl_power_est   )
  g.connect_by_name( signoff,         gl_power_est   )
  g.connect_by_name( vcs_gl_sim,      gl_power_est   )

  #-----------------------------------------------------------------------
  # Parameterize
  #-----------------------------------------------------------------------
  
  g.update_params( adk_parameters )
  g.update_params( parameters )

  return g


if __name__ == '__main__':
  g = construct()
#  g.plot()

