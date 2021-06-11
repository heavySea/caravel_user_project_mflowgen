#=========================================================================
# generate_init_def.py
#=========================================================================
# Generate an initial florrplan for the caravel user project area
# either for the whole wrapper with off-die metal or without for use
# to hard the macro
#
# Author : Maximilian Koschay
# Date   : 02.06.2021

import os

leave_od_metal = os.getenv('leave_od_metal', default=True)

if leave_od_metal:
	import generate_init_def_with_od_metal as generator
	print("Generate initial floorplan .def file including off-die metal.")
	generator.gen_floorplan()
else:
	execfile(generate_init_def_without_od_metal.py)
	import generate_init_def_with_od_metal as generator
	print("Generate initial floorplan .def file wihtout off-die metal.")
	generator.gen_floorplan()