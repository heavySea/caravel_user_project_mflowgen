drc off
snap internal

lef read rtk-tech-nolicon.lef
lef read inputs/adk/stdcells.lef

def read design.def

load $::env(design_name) -dereference

# Extract
extract do local
extract no all
extract all

antennacheck debug
antennacheck

quit
