#-----------------------------------------------------------------------------
# Makefile: compress files for deployment
#
# This makefile requires mpy-cross to create pre-compiled *.mpy files.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# options: override on the command-line
DEPLOY_TO=deploy
CONFIG=src/config.py
LOG_CONFIG=src/log_config.py
SECRETS=src/secrets.py

# make variables from commandline (last invocation)
include makevars.tmp

# all sources
SOURCES=$(wildcard src/*.py)
SPECIAL=src/boot.py src/main.py src/admin.py

# remove files that cannot be precompiled
SOURCES:=$(subst src/boot.py,,${SOURCES})
SOURCES:=$(subst src/main.py,,${SOURCES})
SOURCES:=$(subst src/admin.py,,${SOURCES})
SOURCES:=$(subst src/secrets.py,,${SOURCES})

# remove template files
SOURCES:=$(subst src/sec_template.py,,${SOURCES})
SOURCES:=$(subst src/config_template.py,,${SOURCES})
SOURCES:=$(subst src/log_config_template.py,,${SOURCES})

# sensor-wrappers and task-plugins
SENSORS=$(wildcard src/sensors/*.py)
TASKS=$(wildcard src/tasks/*.py)

# files served by the webserver in admin-mode
WWW=$(wildcard src/www/*)

.PHONY: target_dir check_mpy_cross clean copy2pico

# default target: pre-compile and compress files
default: check_mpy_cross target_dir lib \
	$(SOURCES:src/%.py=${DEPLOY_TO}/%.mpy) \
	$(SPECIAL:src/%.py=${DEPLOY_TO}/%.py) \
	$(SENSORS:src/sensors/%.py=${DEPLOY_TO}/sensors/%.mpy) \
	$(TASKS:src/tasks/%.py=${DEPLOY_TO}/tasks/%.mpy) \
	${DEPLOY_TO}/config.py \
	${DEPLOY_TO}/log_config.py \
	${DEPLOY_TO}/secrets.mpy \
	$(WWW:src/www/%=${DEPLOY_TO}/www/%.gz)
	@rm makevars.tmp
	@make makevars.tmp DEPLOY_TO=${DEPLOY_TO} \
		CONFIG=${CONFIG} \
		LOG_CONFIG=${LOG_CONFIG}

# check for mpy-cross pre-compiler
check_mpy_cross:
	@type -p mpy-cross > /dev/null || \
	  (echo "please install mpy-cross from https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/mpy-cross/" && false)

# create target-directory
target_dir:
	mkdir -p ${DEPLOY_TO}/sensors ${DEPLOY_TO}/tasks ${DEPLOY_TO}/www

# copy libs and fonts
lib:
	rsync -av --delete src/lib ${DEPLOY_TO}
	rsync -av --delete src/fonts ${DEPLOY_TO}

# clean target-directory
clean:
	rm -fr makevars.tmp ${DEPLOY_TO}/*

# recreate makevars.tmp
makevars.tmp:
	@echo -e \
	"DEPLOY_TO=${DEPLOY_TO}\nCONFIG=${CONFIG}\nLOG_CONFIG=${LOG_CONFIG}" > $@

# rsync content of target-directory to pico
# note: this needs a LABEL=CIRCUITPY entry in /etc/fstab and it only works
#       if the CIRCUITPY-drive is not already mounted (e.g. by an automounter)
copy2pico: default
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

${DEPLOY_TO}/secrets.mpy: ${SECRETS}
	mpy-cross $< -o $@

$(SPECIAL:src/%.py=${DEPLOY_TO}/%.py): ${DEPLOY_TO}/%.py: src/%.py
	cp -a $< $@

$(SOURCES:src/%.py=${DEPLOY_TO}/%.mpy): ${DEPLOY_TO}/%.mpy: src/%.py
	mpy-cross $< -o $@

$(SENSORS:src/sensors/%.py=${DEPLOY_TO}/sensors/%.mpy): \
	${DEPLOY_TO}/sensors/%.mpy: src/sensors/%.py
	mpy-cross $< -o $@

$(TASKS:src/tasks/%.py=${DEPLOY_TO}/tasks/%.mpy): \
	${DEPLOY_TO}/tasks/%.mpy: src/tasks/%.py
	mpy-cross $< -o $@

$(WWW:src/www/%=${DEPLOY_TO}/www/%.gz): ${DEPLOY_TO}/www/%.gz: src/www/%
	gzip -9c $< > $@
