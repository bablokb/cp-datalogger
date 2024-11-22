#-----------------------------------------------------------------------------
# Makefile: compress files for deployment
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------
SHELL=/bin/bash
export PATH := ${PATH}:bin
export

# options: override on the command-line
CP_VERSION=8
PCB=v2
DEPLOY_TO=deploy
AP_CONFIG=
SECRETS=src/secrets.py
MAKEVARS=makevars.tmp
CONFIG=src/config.py
LOG_CONFIG=src/log_config.py
FONT=DejaVuSansMono-Bold-18-subset.bdf

ifeq (gateway,$(findstring gateway,${MAKECMDGOALS}))
SRC=src.gateway
SOURCES=$(wildcard src.gateway/*.py)
SOURCES2=src/lora.py src/log_writer.py src/singleton.py src/hw_helper.py \
         src/wifi_impl_builtin.py src/oled.py
SPECIAL=src.gateway/main.py
CONFIG=src.gateway/config.py
LOG_CONFIG=src.gateway/log_config.py
COPY_PREREQ=gateway
else
SRC=src
SOURCES=$(wildcard src/*.py)
SPECIAL=src/boot.py src/main.py src/admin.py src/broadcast.py src/scd4x_config.py
COPY_PREREQ=default
endif

# make variables from commandline (last invocation)
include ${MAKEVARS}

# dynamically create make variables
include dynvars.tmp

# remove files that cannot be precompiled
SOURCES:=$(subst ${SRC}/boot.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/main.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/admin.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/broadcast.py,,${SOURCES})
SOURCES:=$(subst ${SRC}/scd4x_config.py,,${SOURCES})
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

# tools
TOOLS=$(wildcard ./tools/*)

ifneq ($(strip ${AP_CONFIG}),)
ap_config=${DEPLOY_TO}/ap_config.mpy
else
ap_config=
endif

.PHONY: clean copy2pico copy2gateway

# default target: pre-compile and compress files
default: ${DEPLOY_TO} ${DEPLOY_TO}/sensors \
	${DEPLOY_TO}/tasks ${DEPLOY_TO}/tools ${DEPLOY_TO}/www \
        lib ${DEPLOY_TO}/fonts/${FONT} ${ap_config} \
	${DEPLOY_TO}/pins.mpy \
	$(SOURCES:${SRC}/%.py=${DEPLOY_TO}/%.mpy) \
	$(SPECIAL:${SRC}/%.py=${DEPLOY_TO}/%.py) \
	$(SENSORS:${SRC}/sensors/%.py=${DEPLOY_TO}/sensors/%.mpy) \
	$(TOOLS:./tools/%=${DEPLOY_TO}/tools/%) \
	$(TASKS:${SRC}/tasks/%.py=${DEPLOY_TO}/tasks/%.mpy) \
	${DEPLOY_TO}/config.py \
	${DEPLOY_TO}/log_config.py \
	${DEPLOY_TO}/secrets.mpy \
	$(WWW:${SRC}/www/%=${DEPLOY_TO}/www/%.gz) \
	${DEPLOY_TO}/commit.py
	@rm -f makevars.tmp
	@make -e makevars.tmp

gateway: ${DEPLOY_TO} lib \
	${DEPLOY_TO}/pins.mpy \
	${DEPLOY_TO}/secrets.mpy \
	$(SOURCES:${SRC}/%.py=${DEPLOY_TO}/%.mpy) \
	$(SOURCES2:src/%.py=${DEPLOY_TO}/%.mpy) \
	$(SPECIAL:${SRC}/%.py=${DEPLOY_TO}/%.py) \
	${DEPLOY_TO}/config.py \
	${DEPLOY_TO}/log_config.py
	@rm -f makevars.tmp
	@make -e makevars.tmp

# create target-directory
${DEPLOY_TO} ${DEPLOY_TO}/sensors ${DEPLOY_TO}/tasks ${DEPLOY_TO}/tools ${DEPLOY_TO}/www:
	mkdir -p  $@

# copy libs and fonts
lib:
	mkdir -p ${DEPLOY_TO}/lib
	rsync -av --delete ${SRC}/lib${CP_VERSION}/ ${DEPLOY_TO}/lib/
ifneq ($(strip ${USER_LIBS}),)
	rsync -av ${USER_LIBS} ${DEPLOY_TO}/lib
endif

${DEPLOY_TO}/fonts/${FONT}: ${SRC}/fonts/${FONT}
	mkdir -p ${DEPLOY_TO}/fonts
	rsync -av ${SRC}/fonts/${FONT} ${DEPLOY_TO}/fonts/${FONT}

# clean target-directory (only delete auto-created makevars.tmp)
clean:
	rm -fr dynvars.tmp makevars.tmp ${DEPLOY_TO}/* \
	${SRC}/../.commit.py.local

# recreate makevars.tmp
makevars.tmp:
	@echo -e "PCB=${PCB}" > $@
	@echo -e "DEPLOY_TO=${DEPLOY_TO}" >> $@
	@echo -e "CONFIG=${CONFIG}" >> $@
	@echo -e "LOG_CONFIG=${LOG_CONFIG}" >> $@
	@echo -e "AP_CONFIG=${AP_CONFIG}" >> $@
	@echo -e "SECRETS=${SECRETS}" >> $@
	@echo -e "CP_VERSION=${CP_VERSION}" >> $@
	@echo -e "USER_LIBS=${USER_LIBS}" >> $@

dynvars.tmp:
	sed -ne "/^FONT_DISPLAY/s/^FONT_DISPLAY *= *[\"']\([^\"']*\).*$$/FONT=\1.bdf/p" \
        ${CONFIG} >> $@

# rsync content of target-directory to pico
# note: this needs a LABEL=CIRCUITPY entry in /etc/fstab and it only works
#       if the CIRCUITPY-drive is not already mounted (e.g. by an automounter)
copy2pico copy2gateway: ${COPY_PREREQ}
	mount -L CIRCUITPY
	rsync -av -L --inplace --exclude boot_out.txt \
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
	mpy-cross${CP_VERSION} $< -o $@

${DEPLOY_TO}/secrets.mpy: ${SECRETS}
	mpy-cross${CP_VERSION} $< -o $@

ifeq (,$(findstring /,${PCB}))
${DEPLOY_TO}/pins.mpy: ${SRC}/pins${PCB}.py
else
${DEPLOY_TO}/pins.mpy: ${PCB}
endif
	bin/mpy-cross${CP_VERSION} $< -o $@

${DEPLOY_TO}/commit.py: ${SRC}/../.commit.py.local
	cp -a $< $@

${SRC}/../.commit.py.local:
	git log --format="commit='%H'" -n 1 > $@

$(SPECIAL:${SRC}/%.py=${DEPLOY_TO}/%.py): ${DEPLOY_TO}/%.py: ${SRC}/%.py
	cp -a $< $@

$(SOURCES:${SRC}/%.py=${DEPLOY_TO}/%.mpy): ${DEPLOY_TO}/%.mpy: ${SRC}/%.py
	bin/mpy-cross${CP_VERSION} $< -o $@

$(SOURCES2:src/%.py=${DEPLOY_TO}/%.mpy): ${DEPLOY_TO}/%.mpy: src/%.py
	bin/mpy-cross${CP_VERSION} $< -o $@

$(SENSORS:${SRC}/sensors/%.py=${DEPLOY_TO}/sensors/%.mpy): \
	${DEPLOY_TO}/sensors/%.mpy: ${SRC}/sensors/%.py
	bin/mpy-cross${CP_VERSION} $< -o $@

$(TASKS:${SRC}/tasks/%.py=${DEPLOY_TO}/tasks/%.mpy): \
	${DEPLOY_TO}/tasks/%.mpy: ${SRC}/tasks/%.py
	bin/mpy-cross${CP_VERSION} $< -o $@

$(WWW:${SRC}/www/%=${DEPLOY_TO}/www/%.gz): ${DEPLOY_TO}/www/%.gz: ${SRC}/www/%
	gzip -9c $< > $@

$(TOOLS:./tools/%.py=${DEPLOY_TO}/tools/%.py): \
         ${DEPLOY_TO}/tools/%.py: ./tools/%.py
	cp -a $< $@
