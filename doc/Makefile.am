EXTRA_DIST = $(man_MANS)
DISTCLEANFILES = $(man_MANS)

all-local: reference

if HAVE_EPYDOC
reference: $(top_srcdir)/paisleycmd/*.py
	epydoc -o reference $(top_srcdir)/paisleycmd
else
reference:
	@true
endif

man_MANS = paisley.1

paisley.1: $(top_srcdir)/paisleycmd/extern/python-command/scripts/help2man $(top_srcdir)/paisleycmd
	PYTHONPATH=$(top_srcdir) $(PYTHON) $(top_srcdir)/paisleycmd/extern/python-command/scripts/help2man paisleycmd.command.main.Paisley paisley > paisley.1

clean-local:
	@rm -rf reference
