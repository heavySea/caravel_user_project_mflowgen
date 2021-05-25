# Caravel User Project for the use of mflowgen with commercial EDA tools

This repository provides a template ASIC implementation flow using commercial EDA tools using the flow generator mflowgen for the Google/efabless caravel MWP program.

mflowgen is a modular flow specification and build-system generator that can be used to define implementation steps for both ASIC and FPGA designs and any Process design kit, including the Skywater open-source PDK.

## Features

Following features have been implemented so far:

- Basic implementation flow for the user_project_wrapper using Synopsys DC for synthesis, Cadence Innovus for PnR, Magic and Netgen for DRC and LVS
- Initial floorplan file for the user_project_wrapper for full power/ground design capabilities in Cadence Innovus
- Integrated into the MWP caravel user project wrapper 
- Additional single-command automation to install and setup all repository dependencies
	+ mflowgen
	+ skywater-130-nm ADK (mflowgen's PDK view) with fully automated file setup
	+ PDK, openLane, ... dependencies already provided by the source repository
- Single-command to build and clean implementation flows


Planned features are:
- Basic RTL and GL simulation flows using Mentor Modelsim and Power Estimation using Synopsys PrimeTime PX/PrimePower

## Installation


## mflowgen usage

## Verification

## Initial Floorplan

## Changelog

For now only the changes are listed:
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
