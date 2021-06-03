# This file is a quick setup script which can be used to initialize the mflowgen enviroment
# It is intended to be copied each build folder
# The variable MFLOWGEN_ROOT should point to the mflowgen root directory.

export MFLOWGEN_ROOT=../mflowgen

# Path to ADK
export MFLOWGEN_PATH=../SKY130_ADK

source ${MFLOWGEN_ROOT}/venv/bin/activate
