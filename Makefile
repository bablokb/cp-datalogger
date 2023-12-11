#-----------------------------------------------------------------------------
# Makefile: compress files for deployment
#
# This makefile requires mpy-cross to create pre-compiled *.mpy files.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

DEPLOY_TO=deploy

SOURCES=$(wildcard src/*.py)
SOURCES:=$(subst src/main.py,,${SOURCES})
SOURCES:=$(subst src/sec_template.py,,${SOURCES})
SOURCES:=$(subst src/config_template.py,,${SOURCES})
SOURCES:=$(subst src/log_config_template.py,,${SOURCES})

SENSORS=$(wildcard src/sensors/*.py)
TASKS=$(wildcard src/tasks/*.py)
WWW=$(wildcard src/www/*)

.PHONY: clean

all: deploy lib \
	$(SOURCES:src/%.py=${DEPLOY_TO}/%.mpy) \
	$(SENSORS:src/sensors/%.py=${DEPLOY_TO}/sensors/%.mpy) \
	$(TASKS:src/tasks/%.py=${DEPLOY_TO}/tasks/%.mpy) \
	$(WWW:src/www/%=${DEPLOY_TO}/www/%.gz)
	cp -vu --preserve=all src/main.py ${DEPLOY_TO}/

deploy:
	mkdir -p ${DEPLOY_TO}/sensors ${DEPLOY_TO}/tasks ${DEPLOY_TO}/www

lib:
	rsync -av --delete src/lib ${DEPLOY_TO}

clean:
	rm -fr ${DEPLOY_TO}/*

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
