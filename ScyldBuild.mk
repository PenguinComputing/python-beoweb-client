ifneq ($(VERBOSE),0)
$(warning parsing python-beoweb-client/ScyldBuild.mk)
endif

# Variables need to be unique across the entire build, so prefix them with 
# the directory name.
python-beoweb-client_SPEC=python-beoweb-client/python-beoweb-client.spec
python-beoweb-client_ARCHS := x86_64

SPECFILES += $(python-beoweb-client_SPEC)

# create a variable storing the list of targets for this make segment
# so that other packages can manually add their own dependencies easily
python-beoweb-client_TARGETS += $(call add_targets,python-beoweb-client)
BUILD_TARGETS += $(python-beoweb-client_TARGETS)
python-beoweb-client_INSTALL_RPMS := $(call install_some_rpms,python-beoweb-client,'debuginfo')

scyld-python-beoweb-client_VERSION := 0.1.2

$(RPM_SOURCE_DIR)/python-beoweb-client-$(scyld-python-beoweb-client_VERSION).tar.gz: $(shell find python-beoweb-client -print -type f)
	( cd python-beoweb-client ; tar zcf $@ *)

clean::
	$(RM) $(RPM_SOURCE_DIR)/python-beoweb-client-$(scyld-python-beoweb-client_VERSION).tar.gz

