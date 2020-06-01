PKG_DIR     := git_python_utils

PYTHON      := python3
GENVERSION  := gen_version.py
OUTVERSION  := $(PKG_DIR)/version.py

RM          := rm -rf

default: all

all: version
	$(PYTHON) setup.py bdist_wheel

version:
	$(PYTHON) $(GENVERSION) $(OUTVERSION)

clean:
	$(RM) build dist $(PKG_DIR).egg-info
