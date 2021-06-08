# SPDX-FileCopyrightText: 2020 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

#-----------------------------------------------------------------------
# Parameters & Variables
#-----------------------------------------------------------------------

CARAVEL_ROOT?=$(PWD)/caravel
PRECHECK_ROOT?=${PWD}/open_mpw_precheck
SIM ?= RTL

# Install lite version of caravel, (1): caravel-lite, (0): caravel
CARAVEL_LITE?=1

ifeq ($(CARAVEL_LITE),1) 
	CARAVEL_NAME := caravel-lite
	CARAVEL_REPO ?= https://github.com/efabless/caravel-lite 
	CARAVEL_BRANCH ?= main
else
	CARAVEL_NAME := caravel
	CARAVEL_REPO ?= https://github.com/efabless/caravel 
	CARAVEL_BRANCH ?= master
endif

# Install caravel as submodule, (1): submodule, (0): clone
SUBMODULE?=1

# Information about MFLOWGEN
# Repository Branch and Location can be changed!
MFLOWGEN_ROOT ?=$(PWD)/mflowgen/mflowgen
MFLOWGEN_NAME ?= mflowgen
MFLOWGEN_REPO ?= https://github.com/mflowgen/mflowgen
MFLOWGEN_BRANCH ?= master

# The mflowgen ADK for Skywater130 PDK
# path is fixed
SKY_ADK_PATH ?= $(PWD)/mflowgen/SKY130_ADK
SKY_ADK_REPO ?= https://github.com/heavySea/skywater-130nm-adk
SKY_ADK_BRANCH ?= master

M_FLOWS := $(PWD)/mflowgen/flows

MFLOWGEN_INTERACTIVE_FLOW ?= 0

#-----------------------------------------------------------------------
# Mflowgen and openlane build targets
#-----------------------------------------------------------------------

# Include Caravel Makefile Targets
.PHONY: %
%: 
	$(MAKE) -f $(CARAVEL_ROOT)/Makefile $@

# Verify Target for running simulations
.PHONY: verify
verify:
	cd ./verilog/dv/ && \
	export SIM=${SIM} && \
		$(MAKE) -j$(THREADS)

# Install DV setup
.PHONY: simenv
simenv:
	docker pull efabless/dv_setup:latest

PATTERNS=$(shell cd verilog/dv && find * -maxdepth 0 -type d)
DV_PATTERNS = $(foreach dv, $(PATTERNS), verify-$(dv))
TARGET_PATH=$(shell pwd)
PDK_PATH=${PDK_ROOT}/sky130A
VERIFY_COMMAND="cd ${TARGET_PATH}/verilog/dv/$* && export SIM=${SIM} && make"
$(DV_PATTERNS): verify-% : ./verilog/dv/% 
	docker run -v ${TARGET_PATH}:${TARGET_PATH} -v ${PDK_PATH}:${PDK_PATH} \
                -v ${CARAVEL_ROOT}:${CARAVEL_ROOT} \
                -e TARGET_PATH=${TARGET_PATH} -e PDK_PATH=${PDK_PATH} \
                -e CARAVEL_ROOT=${CARAVEL_ROOT} \
                -u $(id -u $$USER):$(id -g $$USER) efabless/dv_setup:latest \
                sh -c $(VERIFY_COMMAND)
				
# Mflowgen Makefile Targets
BLOCKS = $(shell cd mflowgen/flows && find * -maxdepth 0 -type d)

BUILD_BLOCKS = $(foreach block, $(BLOCKS), mflowgen-$(block))

.PHONY: $(BUILD_BLOCKS)
$(BUILD_BLOCKS): mflowgen-%: mflowgen/build_%
	( \
		export TOP=${MFLOWGEN_ROOT}; \
		cd mflowgen/build_${*}; \
		. $(MFLOWGEN_ROOT)/venv/bin/activate; \
		export MFLOWGEN_PATH=${SKY_ADK_PATH}; \
		mflowgen run --design ${M_FLOWS}/${*}; \
		if [ "${MFLOWGEN_INTERACTIVE_FLOW}" -eq 0 ]; then \
			make; \
		fi )

mflowgen/build_%:
	mkdir $@ 
	cp mflowgen/flows/sourceme_mflowgen_env.sh $@
	sed "s|export MFLOWGEN_ROOT=.*|export MFLOWGEN_ROOT=${MFLOWGEN_ROOT}|g" -i $@/sourceme_mflowgen_env.sh
	sed "s|export MFLOWGEN_PATH=.*|export MFLOWGEN_PATH=${SKY_ADK_PATH}|g" -i $@/sourceme_mflowgen_env.sh
	chmod a+x $@/sourceme_mflowgen_env.sh

CLEAN_BLOCKS = $(foreach block, $(BLOCKS), clean-$(block))
#.PHONY: clean_$(BLOCKS)
$(CLEAN_BLOCKS): clean-% :
	rm -rf mflowgen/build_$*


# Openlane Makefile Targets
OL_BLOCKS = $(shell cd openlane && find * -maxdepth 0 -type d)
OL_BUILD_BLOCKS = $(foreach block, $(OL_BLOCKS), openlane-$(block))
.PHONY: $(OL_BUILD_BLOCKS)
$(OL_BUILD_BLOCKS): openlane-%:
	cd openlane && $(MAKE) $*

.PHONY: install
install: install_caravel install_mflowgen install_ADK

#-----------------------------------------------------------------------
# Installation targets, etc.
#-----------------------------------------------------------------------


# Install caravel
.PHONY: install_caravel
install_caravel:
ifeq ($(SUBMODULE),1)
	@echo "Installing $(CARAVEL_NAME) as a submodule.."
# Convert CARAVEL_ROOT to relative path because .gitmodules doesn't accept '/'
	$(eval CARAVEL_PATH := $(shell realpath --relative-to=$(shell pwd) $(CARAVEL_ROOT)))
	@if [ ! -d $(CARAVEL_ROOT) ]; then git submodule add --name $(CARAVEL_NAME) $(CARAVEL_REPO) $(CARAVEL_PATH); fi
	@git submodule update --init $(CARAVEL_PATH)
	@cd $(CARAVEL_ROOT); git checkout $(CARAVEL_BRANCH)
	$(MAKE) simlink
else
	@echo "Installing $(CARAVEL_NAME).."
	@git clone $(CARAVEL_REPO) $(CARAVEL_ROOT)
	@cd $(CARAVEL_ROOT); git checkout $(CARAVEL_BRANCH)
endif

.PHONY: install_mflowgen
install_mflowgen:
	# Install mflowgen as submodule
	@echo "Installing $(MFLOWGEN_NAME) as a submodule.."
# Convert CARAVEL_ROOT to relative path because .gitmodules doesn't accept '/'
	$(eval MFLOWGEN_PATH := $(shell realpath --relative-to=$(shell pwd) $(MFLOWGEN_ROOT)))
	@if [ ! -d $(MFLOWGEN_ROOT) ]; then git submodule add --name $(MFLOWGEN_NAME) $(MFLOWGEN_REPO) $(MFLOWGEN_PATH); fi
	@git submodule update --init $(MFLOWGEN_PATH)
	cd $(MFLOWGEN_ROOT); git checkout $(MFLOWGEN_BRANCH)
	$(MAKE) install_mflowgen_venv

# Create symbolic links to caravel's main files
.PHONY: simlink
simlink: check-caravel
### Symbolic links relative path to $CARAVEL_ROOT 
	$(eval MAKEFILE_PATH := $(shell realpath --relative-to=openlane $(CARAVEL_ROOT)/openlane/Makefile))
	$(eval PIN_CFG_PATH  := $(shell realpath --relative-to=openlane/user_project_wrapper $(CARAVEL_ROOT)/openlane/user_project_wrapper_empty/pin_order.cfg))
	mkdir -p openlane
	mkdir -p openlane/user_project_wrapper
	cd openlane &&\
	ln -sf $(MAKEFILE_PATH) Makefile
	cd openlane/user_project_wrapper &&\
	ln -sf $(PIN_CFG_PATH) pin_order.cfg

# Install mflowgen virtual enviroment
.PHONY: install_mflowgen_venv
install_mflowgen_venv: check-mflowgen
	cd $(MFLOWGEN_ROOT)
	@echo "Installing virtual pyhon enviroment for $(MFLOWGEN_NAME)"; 
	( \
		export TOP=${MFLOWGEN_ROOT}; \
		cd $(MFLOWGEN_ROOT); \
		python3 -m venv venv; \
		. $(MFLOWGEN_ROOT)/venv/bin/activate; \
		pip install -e .; )

export PDK_ROOT

.PHONY: install_ADK
install_ADK: check-pdk
	@echo "Installing mflowgen Skywater ADK as a submodule in $(SKY_ADK_PATH)"
	$(eval ADK_PATH := $(shell realpath --relative-to=$(shell pwd) $(SKY_ADK_PATH)))
	@if [ ! -d $(SKY_ADK_PATH) ]; then git submodule add --name SKY130_ADK $(SKY_ADK_REPO) $(ADK_PATH); fi
	@git submodule update --init $(ADK_PATH)
	cd $(SKY_ADK_PATH); git checkout $(SKY_ADK_BRANCH)
	cd $(SKY_ADK_PATH) && $(MAKE) install

# Update Caravel
.PHONY: update_caravel
update_caravel: check-caravel
ifeq ($(SUBMODULE),1)
	@git submodule update --init --recursive $(CARAVEL_ROOT)
	cd $(CARAVEL_ROOT) && \
	git checkout $(CARAVEL_BRANCH) && \
	git pull
else
	cd $(CARAVEL_ROOT)/ && \
		git checkout $(CARAVEL_BRANCH) && \
		git pull
endif

# Update mflowgen
.PHONY: update_mflowgen
update_mflowgen: check-mflowgen
	@git submodule update --init --recursive $(MFLOWGEN_ROOT)
	cd $(MFLOWGEN_ROOT) && \
	git checkout $(MFLOWGEN_BRANCH) && \
	git pull

# Update SKY ADK
.PHONY: update_ADK
update_ADK: check-ADK
	@git submodule update --init --recursive $(SKY_ADK_PATH)
	cd $(SKY_ADK_PATH) && \
	git checkout $(SKY_ADK_BRANCH) && \
	git pull
	cd $(SKY_ADK_PATH) && $(MAKE) install

.PHONY: uninstall
uninstall: uninstall_caravel uninstall_mflowgen uninstall_ADK

# Uninstall Caravel
.PHONY: uninstall_caravel
uninstall_caravel: check-caravel
	# Caravel
ifeq ($(SUBMODULE),1)
	git config -f .gitmodules --remove-section "submodule.$(CARAVEL_NAME)"
	git add .gitmodules
	git submodule deinit -f $(CARAVEL_ROOT)
	git rm --cached $(CARAVEL_ROOT)
	rm -rf .git/modules/$(CARAVEL_NAME)
	rm -rf $(CARAVEL_ROOT)
else
	rm -rf $(CARAVEL_ROOT)
endif

# Uninstall Mflowgen
.PHONY: uninstall_mflowgen
uninstall_mflowgen: check-mflowgen
	git config -f .gitmodules --remove-section "submodule.$(MFLOWGEN_NAME)"
	git config -f .git/config --remove-section "submodule.$(MFLOWGEN_NAME)"
	git add .gitmodules
	git submodule deinit -f $(MFLOWGEN_ROOT)
	git rm -f --cached $(MFLOWGEN_ROOT)
	rm -rf .git/modules/$(MFLOWGEN_NAME)
	# only remove mflowgen root when in this repository
ifeq ($(MFLOWGEN_ROOT),$(PWD)/mflowgen/mflowgen)
	rm -rf $(MFLOWGEN_ROOT)
endif

# Uninstall ADK
.PHONY: uninstall_ADK
uninstall_ADK: check-ADK
	git config -f .gitmodules --remove-section "submodule.SKY130_ADK"
	git config -f .git/config --remove-section "submodule.SKY130_ADK"
	git add .gitmodules
	git submodule deinit -f $(SKY_ADK_PATH)
	git rm -f --cached $(SKY_ADK_PATH)
	rm -rf .git/modules/$(SKY130_ADK)
	rm -rf $(SKY_ADK_PATH)
	

# Install Openlane
.PHONY: openlane
openlane: 
	cd openlane && $(MAKE) openlane

# Install Pre-check
# Default installs to the user home directory, override by "export PRECHECK_ROOT=<precheck-installation-path>"
.PHONY: precheck
precheck:
	@git clone https://github.com/efabless/open_mpw_precheck.git --depth=1 $(PRECHECK_ROOT)
	@docker pull efabless/open_mpw_precheck:latest

.PHONY: run-precheck
run-precheck: check-precheck check-pdk check-caravel
	$(eval TARGET_PATH := $(shell pwd))
	cd $(PRECHECK_ROOT) && \
	docker run -v $(PRECHECK_ROOT):/usr/local/bin -v $(TARGET_PATH):$(TARGET_PATH) -v $(PDK_ROOT):$(PDK_ROOT) -v $(CARAVEL_ROOT):$(CARAVEL_ROOT) \
	-u $(shell id -u $(USER)):$(shell id -g $(USER)) efabless/open_mpw_precheck:latest bash -c "python3 open_mpw_prechecker.py --pdk_root $(PDK_ROOT) --target_path $(TARGET_PATH) -rfc -c $(CARAVEL_ROOT) "

# Install PDK using OL's Docker Image
.PHONY: pdk-nonnative
pdk-nonnative: skywater-pdk skywater-library skywater-timing open_pdks
	docker run --rm -v $(PDK_ROOT):$(PDK_ROOT) -v $(pwd):/user_project -v $(CARAVEL_ROOT):$(CARAVEL_ROOT) -e CARAVEL_ROOT=$(CARAVEL_ROOT) -e PDK_ROOT=$(PDK_ROOT) -u $(shell id -u $(USER)):$(shell id -g $(USER)) efabless/openlane:current sh -c "cd $(CARAVEL_ROOT); make build-pdk; make gen-sources"


# Clean 
.PHONY: clean
clean:
	cd ./verilog/dv/ && \
		$(MAKE) -j$(THREADS) clean

check-caravel:
	@if [ ! -d "$(CARAVEL_ROOT)" ]; then \
		echo "Caravel Root: "$(CARAVEL_ROOT)" doesn't exists, please export the correct path before running make. "; \
		exit 1; \
	fi

check-mflowgen:
	@if [ ! -d "$(MFLOWGEN_ROOT)" ]; then \
		echo "Mflowgen Root: "$(MFLOWGEN_ROOT)" doesn't exists, please export the correct path before running make. "; \
		exit 1; \
	fi

check-ADK:
	@if [ ! -d "$(SKY_ADK_PATH)" ]; then \
		echo "Mflowgen Root: "$(SKY_ADK_PATH)" doesn't exists, please export the correct path before running make. "; \
		exit 1; \
	fi

check-precheck:
	@if [ ! -d "$(PRECHECK_ROOT)" ]; then \
		echo "Pre-check Root: "$(PRECHECK_ROOT)" doesn't exists, please export the correct path before running make. "; \
		exit 1; \
	fi

check-pdk:
	@if [ ! -d "$(PDK_ROOT)" ]; then \
		echo "PDK Root: "$(PDK_ROOT)" doesn't exists, please export the correct path before running make. "; \
		exit 1; \
	fi

.PHONY: help
help:
	cd $(CARAVEL_ROOT) && $(MAKE) help 
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
