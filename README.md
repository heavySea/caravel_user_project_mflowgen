# Caravel User Project for the use of mflowgen with commercial EDA tools


Readme is on the todo list...

For now only the changes are listed:
- Install mflowgen as submodule and virtual enviroment using Make
	Change mflowgen repository by setting
	- MFLOWGEN_REPO url and MFLOWGEN_BRANCH
	- MFLOWGEN_NAME can also be changed
	- If mflowgen is already installed on the disk you can also change MFLOWGEN_ROOT

- Installing ADK using Make
	Change SKY130 ADK repository by settings
	- SKY_ADK_REPO ur and SKY_ADK_BRANCH
	- the Path and name of the repository is fixed to mflowgen/SKY130_ADK
- Automate the ADK standard view
	- Copy more files from the open-pdk generated files
	- Newly generated files for Synopsys and Cadence tools are copied into the PDK for reuse


