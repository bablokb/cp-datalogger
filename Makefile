#-----------------------------------------------------------------------------
# Makefile: compress files for deployment
#
# This makefile requires mpy-cross to create pre-compiled *.mpy files.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------
SHELL=/bin/bash

# options: override on the command-line
PCB=v2
DEPLOY_TO=deploy
AP_CONFIG=
SECRETS=src/secrets.py
MAKEVARS=makevars.tmp
CONFIG=src/config.py
LOG_CONFIG=src/log_config.py

ifeq (gateway,$(findstring gateway,${MAKECMDGOALS}))
SRC=src.blues_gateway
SOURCES=$(wildcard src.blues_gateway/*.py)
SOURCES2=src/lora.py src/log_writer.py src/singleton.py
SPECIAL=src.blues_gateway/main.py
CONFIG=src.blues_gateway/config.py
LOG_CONFIG=src.blues_gateway/log_config.py
COPY_PREREQ=gateway
else
SRC=src
SOURCES=$(wildcard src/*.py)
SPECIAL=src/boot.py src/main.py src/admin.py src/broadcast.py
COPY_PREREQ=default
endif

# make variables from commandline (last invocation)
include ${MAKEVARS}

# remove files that cannot be precompiled
SOURCES:=$(subst ${SRC}/boot.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/main.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/admin.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/broadcast.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/secrets.py,,${SOURCES})

# remove template files
SOURCES:=$(subst ${SRC}/sec_template.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/config_template.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/log_config_template.py,,${SOURCES})

# sensor-wrappers and task-plugins
SENSORS=$(wildcard ${SRC}/sensors/*.py)
TASKS=$(wildcard ${SRC}/tasks/*.py)

# files served by the webserver in admin-mode
WWW=$(wildcard ${SRC}/www/*)

ifneq ($(strip ${AP_CONFIG}),)
ap_config=${DEPLOY_TO}/ap_config.mpy
else
ap_config=
endif

.PHONY: check_mpy_cross clean copy2pico copy2gateway

# default target: pre-compile and compress files
default: check_mpy_cross ${DEPLOY_TO} ${DEPLOY_TO}/sensors \
	${DEPLOY_TO}/tasks ${DEPLOY_TO}/www lib fonts ${ap_config} \
	${DEPLOY_TO}/pins.mpy \
	$(SOURCES:${SRC}/%.py=${DEPLOY_TO}/%.mpy) \
	$(SPECIAL:${SRC}/%.py=${DEPLOY_TO}/%.py) \
	$(SENSORS:${SRC}/sensors/%.py=${DEPLOY_TO}/sensors/%.mpy) \
	$(TASKS:${SRC}/tasks/%.py=${DEPLOY_TO}/tasks/%.mpy) \
	${DEPLOY_TO}/config.py \
	${DEPLOY_TO}/log_config.py \
	${DEPLOY_TO}/secrets.mpy \
	$(WWW:${SRC}/www/%=${DEPLOY_TO}/www/%.gz)
	@git log --format="commit='%H'" -n 1 > ${DEPLOY_TO}/commit.py
	@rm -f makevars.tmp
	@make makevars.tmp PCB=${PCB} DEPLOY_TO=${DEPLOY_TO} \
		CONFIG=${CONFIG} AP_CONFIG=${AP_CONFIG} \
		LOG_CONFIG=${LOG_CONFIG}

gateway: check_mpy_cross ${DEPLOY_TO} lib \
	${DEPLOY_TO}/pins.mpy \
	$(SOURCES:${SRC}/%.py=${DEPLOY_TO}/%.mpy) \
	$(SOURCES2:src/%.py=${DEPLOY_TO}/%.mpy) \
	$(SPECIAL:${SRC}/%.py=${DEPLOY_TO}/%.py) \
	${DEPLOY_TO}/config.py \
	${DEPLOY_TO}/log_config.py
	@rm -f makevars.tmp
	@make makevars.tmp PCB=${PCB} DEPLOY_TO=${DEPLOY_TO} \
		CONFIG=${CONFIG} AP_CONFIG=${AP_CONFIG} \
		LOG_CONFIG=${LOG_CONFIG}

# check for mpy-cross pre-compiler
check_mpy_cross:
	@type -p mpy-cross > /dev/null || \
	  (echo "please install mpy-cross from https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/mpy-cross/" && false)

# create target-directory
${DEPLOY_TO} ${DEPLOY_TO}/sensors ${DEPLOY_TO}/tasks ${DEPLOY_TO}/www:
	mkdir -p  $@

# copy libs and fonts
lib:
	rsync -av --delete ${SRC}/lib ${DEPLOY_TO}
fonts:
	rsync -av --delete ${SRC}/fonts ${DEPLOY_TO}

# clean target-directory (only delete auto-created makevars.tmp)
clean:
	rm -fr makevars.tmp ${DEPLOY_TO}/*

# recreate makevars.tmp
makevars.tmp:
	@echo -e \
	"PCB=${PCB}\nDEPLOY_TO=${DEPLOY_TO}\nCONFIG=${CONFIG}\nLOG_CONFIG=${LOG_CONFIG}\nAP_CONFIG=${AP_CONFIG}\nSECRETS=${SECRETS}" > $@

# rsync content of target-directory to pico
# note: this needs a LABEL=CIRCUITPY entry in /etc/fstab and it only works
#       if the CIRCUITPY-drive is not already mounted (e.g. by an automounter)
copy2pico copy2gateway: ${COPY_PREREQ}
	mount -L CIRCUITPY
	rsync -av -L --exclude boot_out.txt \
		--exclude  __pycache__ \
		--no-owner --no-group --delete \
		--modify-window=2 "${DEPLOY_TO}/" \
		$$(findmnt -S LABEL=CIRCUITPY -no TARGET)/
	sync
	umount $$(findmnt -S LABEL=CIRCUITPY -no TARGET)

${DEPLOY_TO}/config.py: ${CONFIG}
	cp -a $< $@

${DEPLOY_TO}/log_config.py: ${LOG_CONFIG}
	cp -a $< $@

${DEPLOY_TO}/ap_config.mpy: ${AP_CONFIG}
	mpy-cross $< -o $@

${DEPLOY_TO}/secrets.mpy: ${SECRETS}
	mpy-cross $< -o $@

ifeq (,$(findstring /,${PCB}))
${DEPLOY_TO}/pins.mpy: ${SRC}/pins${PCB}.py
else
${DEPLOY_TO}/pins.mpy: ${PCB}
endif
	mpy-cross $< -o $@


$(SPECIAL:${SRC}/%.py=${DEPLOY_TO}/%.py): ${DEPLOY_TO}/%.py: ${SRC}/%.py
	cp -a $< $@

$(SOURCES:${SRC}/%.py=${DEPLOY_TO}/%.mpy): ${DEPLOY_TO}/%.mpy: ${SRC}/%.py
	mpy-cross $< -o $@

$(SOURCES2:src/%.py=${DEPLOY_TO}/%.mpy): ${DEPLOY_TO}/%.mpy: src/%.py
	mpy-cross $< -o $@

$(SENSORS:${SRC}/sensors/%.py=${DEPLOY_TO}/sensors/%.mpy): \
	${DEPLOY_TO}/sensors/%.mpy: ${SRC}/sensors/%.py
	mpy-cross $< -o $@

$(TASKS:${SRC}/tasks/%.py=${DEPLOY_TO}/tasks/%.mpy): \
	${DEPLOY_TO}/tasks/%.mpy: ${SRC}/tasks/%.py
	mpy-cross $< -o $@

$(WWW:${SRC}/www/%=${DEPLOY_TO}/www/%.gz): ${DEPLOY_TO}/www/%.gz: ${SRC}/www/%
	gzip -9c $< > $@
