# Caravel User Project for the use of mflowgen with commercial EDA tools

This repository provides a template ASIC implementation flow for commercial EDA tools using the flow generator [mflowgen](https://github.com/mflowgen/mflowgen) for the [Google/efabless caravel MWP program](https://www.efabless.com/open_shuttle_program/2).

[mflowgen](https://github.com/mflowgen/mflowgen) is a modular flow specification and build-system generator that can be used to define implementation steps for both ASIC and FPGA designs using any process design kit, including the [Skywater open-source PDK](https://github.com/google/skywater-pdk).

## Features

Following features have been implemented so far:

- Basic implementation flow for the user_project_wrapper using Synopsys DC for synthesis, Cadence Innovus for PnR, Magic and Netgen for DRC and LVS
- Initial floorplan file for the user_project_wrapper for full power/ground design capabilities in Cadence Innovus
- Additional single-command automation to install and setup all repository dependencies
	+ mflowgen
	+ skywater-130-nm ADK (mflowgen's PDK view) with fully automated file setup
	+ PDK, openLane, ... dependencies already provided by the source repository
- Single-command to build and clean implementation flows

Planned features are:
- Basic RTL and GL simulation flows using Mentor Modelsim and Power Estimation using Synopsys PrimeTime PX/PrimePower

## Installation

To setup the caravel user project run the following steps.

1. Clone the repository
	```
	git clone https://github.com/efabless/caravel_user_project.git
	cd caravel_user_project
	```

2. Install the PDK
	
	The mflowgen ADK view for the Skywater 130nm process requires files from both the google/skywater-pdk repository as well as RTimothyEdwards/pen_pdks installation. The original caracel_user_project repository already provides a automated installation process.
	Refer to the original Readme for build instructions:
	https://caravel-user-project.readthedocs.io/en/latest/#building-the-pdk
	Make sure to have the `PDK_ROOT` environment variable set all of the time.

3. Install all dependencies

	(Optional) Following installation paths and source links for the caravel, sky-130nm-adk and mflowgen can be configured:
	+ Caravel:
		* Change the the install path with `CARAVEL_ROOT`, by default the caravel will be installed at `$(pwd)/caravel`
		* By default use the caravel-lite repository, otherwise run `export CARAVEL_LITE=0`
		* Change the caravel repository source with `CARAVEL_REPO`, by default the original repository from efabless is used
		* Change the caravel repository branch with `CARAVEL_BRANCH`, by default the master branch will be used 
    + OpenLane:
		* Change the the install path with `OPENLANE_ROOT`, by default the caravel will be installed at `$(pwd)/caravel`
		* By default use the caravel-lite repository, otherwise run `export CARAVEL_LITE=0`
	+ mflowgen:
		* Change the the install path with `MFLOWGEN_ROOT`, by default mflowgen will be installed at `$(pwd)/mflowgen/mflowgen`
		* Change the mflowgen repository source with `MFLOWGEN_REPO`, by default the [original repository](https://github.com/mflowgen/mflowgen)
		* Change the mflowgen repository branch with `MFLOWGEN_BRANCH`, by default the master branch will be used  
	+ sky-130nm-adk:
		* Change the the install path with `SKY_ADK_PATH`, by default the ADK will be installed at `$(pwd)/mflowgen/SKY130_ADK`
		* Change the ADK repository source with `SKY_ADK_REPO`, by default the [ADK repository with the automated installation process](https://github.com/heavySea/skywater-130nm-adk)
		* Change the ADK repository branch with `SKY_ADK_BRANCH`, by default the master branch will be used  

	Finally you can run
	```
	make install
	```

	This will clone all repository dependencies, setup the the ADK and install the mflowgen virtual environment.

5. Install Openlane

	OpenLane has been preserved to be used as well. So you can e.g. harden a macro using mflowgen, export the results and harden the caravel\_user\_project_wrapper with OpenLane.

	First set the path where openLane is/was installed as well as the repository tag to use and install openlane:
	```
	export OPENLANE_ROOT=<openlane-installation-path>
	export OPENLANE_TAG=<latest-openlane-tag>
	make openlane
	```

4. Single dependency installation, update and removal

	You can install all dependencies individually
	```
	make install_caravel
	make install_mflowgen
	make install_ADK
	```
	You can update all dependencies individually
	```
	make update_caravel
	make update_mflowgen
	make update_ADK
	```

	You can remove all dependencies or individually
	```
	## Remove all dependencies
	make uninstall
	## Remove a single dependency
	make uninstall_caravel
	make uninstall_mflowgen
	make uninstall_ADK
	```


## Mflowgen usage

## Caravel user project wrapper hardening with mflowgen

When hardening the `user_project_wrapper` using other tools than openLane the IO pin positions and metal rings must be the same for caravel integration. 
An easy way to assure equivalence is to use the empty floorplan of the wrapper from the openlane flow which is saved as .def file as an inital floorplan.
The 10th step of openlane generates a file called 10-pdn.def which ist the result of the last floorplan step.

Although, the floorplan already contain stripes across the whole die. To enable whole control over power planing, e.g. to create internal power rings for macros, multiple power domains, etc. the stripes have been cut of to the lenght of the regular IO pins. Later on new stripes of all or selected power nets can be generated using Innovus.

The flow script for the `user_project_wrapper` contains the step `caravel-uprj-floorplan` which generates the initial floorplan for Innovus from the openlane floorplan file. It supplies the result to both the innovus-flowesetup and innovus-init step. Moreover it needs to modify the innovus foundation-flow setup.tcl script as well as the script order and the floorplan.tcl script of the innovus-init step. This is done in the construct.py script:

```
init_order = caravel_upr_floorplan.get_param('iInit_order')
init.update_params({'order' : init_order})

iflow.extend_inputs(['setup.tcl'])
iflow.extend_inputs(['user_project_wrapper.def'])
init.extend_inputs(['user_project_wrapper.def', 'floorplan.tcl'])
``` 

More details about hardening the wrapper and macros and openlane refer to the README(TODO).

Hardening the wrapper is still expiremental and not fully verified yet.
Of course you can just harden your design as macros using mflowgen and use openlane to harden the wrapper which is the recommended way by efabless.

## Openlane usage

The process to use openlane has not been changed except for the name of the make target. Once openlane is setup you cann harden macros and the wrapper by

```
# Run openlane to harden user_proj_example
make openlane-user_proj_example
# Run openlane to harden user_project_wrapper
make openlane-user_project_wrapper
```
For more details on openlane, refer to the [openlane README](https://github.com/efabless/caravel/blob/master/openlane/README.rst).

## Verification

The mflowgen implementation flow for the user\_project_wrapper contains DRC and LVS verification steps using Magic and netgen. This should be similar to the verification checks done in the precheck. Once the implementation results have been exported from the mflowgen build directory to the caravel user project repository structure, all pre-check targets should work as well. So you cann run all check-targets mentioned in the [original README](https://caravel-user-project.readthedocs.io/en/latest/#other-miscellaneous-targets).

Currently timing sign-off is only done in Innovus, but planned to be done in Synopsys Spyglass.

## Full-Chip Simulation

Currently using the default Icarus Verilog based simulation. See the [origignal README](https://caravel-user-project.readthedocs.io/en/latest/#running-full-chip-simulation).

Planned to be extended with Mentor Modelsim simulations.

## Changelog

- Install mflowgen as submodule and virtual enviroment using Make
	
    Change mflowgen repository by setting
	- MFLOWGEN_REPO url and MFLOWGEN_BRANCH
	- MFLOWGEN_NAME can also be changed
	- If mflowgen is already installed on the disk you can also change MFLOWGEN_ROOT, default directory is mflowgen/mflowgen

- Installing ADK using Make
	
    Change SKY130 ADK repository by settings
	- SKY_ADK_REPO ur and SKY_ADK_BRANCH
	- If the ADK is already installed on the disk you can also change SKY_ADK_PATH, default directory is mflowgen/SKY130_ADK

-  [Automate the ADK standard view installation](https://github.com/heavySea/skywater-130nm-adk)
	- Copy more files from the open-pdk generated files
	- Newly generated files for Synopsys and Cadence tools are copied into the PDK for reuse

- main Makefile includes targets to build the design with mflowgen
	- targets are generated from directory names in mflowgen/flows
	- builds are done under mflowgen/build_*
- To ease macro placement and hierarchical designs the target designed should be hardened together with the wrapper
	- this requires to follow the initial floorplan exactly
- use the last generated .def file of the openlange floorplanning stage as initial def file in innovus
	- automatically has the right die dimensions, io placement and power rings
	- the mflowgen step "caravel_uprj_floorplan" provides a script to remove power/ground stripes and vias over the core area
