# Read design
gds read inputs/design-merged.gds
load $::env(design_name)

# Count number of DRC errors
drc catchup
drc count

quit
