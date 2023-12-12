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

.PHONY: deploy check_mpy_cross clean

default: check_mpy_cross deploy lib \
	$(SOURCES:src/%.py=${DEPLOY_TO}/%.mpy) \
	$(SENSORS:src/sensors/%.py=${DEPLOY_TO}/sensors/%.mpy) \
	$(TASKS:src/tasks/%.py=${DEPLOY_TO}/tasks/%.mpy) \
	$(WWW:src/www/%=${DEPLOY_TO}/www/%.gz)
	@cp -vu --preserve=all \
		src/boot.py src/main.py src/admin.py ${DEPLOY_TO}/
	@cp -vu --preserve=all ${CONFIG} ${DEPLOY_TO}/config.py
	@cp -vu --preserve=all ${LOG_CONFIG} ${DEPLOY_TO}/log_config.py
	mpy-cross ${SECRETS} -o ${DEPLOY_TO}/secrets.mpy
	@rm makevars.tmp
	@make makevars.tmp DEPLOY_TO=${DEPLOY_TO} \
		CONFIG=${CONFIG} \
		LOG_CONFIG=${LOG_CONFIG}

check_mpy_cross:
	@type -p mpy-cross > /dev/null || \
	  (echo "please install mpy-cross from https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/mpy-cross/" && false)

deploy:
	mkdir -p ${DEPLOY_TO}/sensors ${DEPLOY_TO}/tasks ${DEPLOY_TO}/www

lib:
	rsync -av --delete src/lib ${DEPLOY_TO}
	rsync -av --delete src/fonts ${DEPLOY_TO}

clean:
	rm -fr makevars.tmp ${DEPLOY_TO}/*

makevars.tmp:
	@echo -e \
	"DEPLOY_TO=${DEPLOY_TO}\nCONFIG=${CONFIG}\nLOG_CONFIG=${LOG_CONFIG}" > $@

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
