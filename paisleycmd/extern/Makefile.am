CLEANFILES = *.py{c,o} command/*.py{c,o} log/*.py{c,o}

paisleycmddir = $(PYTHONLIBDIR)/paisleycmd/extern

paisleycmd_PYTHON = \
	__init__.py

logdir = $(PYTHONLIBDIR)/paisleycmd/extern/log

log_PYTHON = \
	log/__init__.py \
	log/log.py

commanddir = $(PYTHONLIBDIR)/paisleycmd/extern/command

command_PYTHON = \
	command/__init__.py \
	command/command.py \
	command/tcommand.py

paisleydir = $(PYTHONLIBDIR)/paisleycmd/extern/paisley

paisley_PYTHON = \
	paisley/__init__.py \
	paisley/changes.py \
	paisley/client.py \
	paisley/mapping.py \
	paisley/pjson.py \
	paisley/views.py

EXTRA_DIST = python-command/scripts/help2man

log:
	make git-submodule
command:
	make git-submodule

git-submodule:
	cd $(top_srcdir) && git submodule init && git submodule sync && git submodule update

.PHONY: git-submodule


all-local: log command
