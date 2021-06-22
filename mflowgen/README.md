# Mflowgen subdirectory

This directory contains all mflowgen dependencies, flow specifications and build folders.

### Contents:

- `flows` directory

    Contains all flow specifications that can be generated in the root directory with `make mflowgen-*`

- `common_mflowgen_step`

    Contains common steps used in more than one flow specification such as DRC, LVS and Export steps

- `mflowgen`

    Mflowgen git submodule.
    https://github.com/mflowgen/mflowgen

- `SKY130_ADK`

    Mflowgen ADK view for the Skywater 130nm PDK
    https://github.com/heavySea/skywater-130nm-adk

- `build_*`

    Generated build directory for any implementation flow. The build folder is not synced with the git repository!