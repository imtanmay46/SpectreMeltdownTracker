# Makefile for SpectreMeltdownTracker

# Variables
LIB_MAKEFILE := lib/Makefile

# Targets
all: run_lib_python

run_lib_python:
	@$(MAKE) -C lib
	@python3 vuln_tracker.py

.PHONY: all run_lib_python
