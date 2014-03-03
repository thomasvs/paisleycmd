completiondir = $(sysconfdir)/bash_completion.d
completion_DATA = paisley

BUILT_SOURCES = paisley
CLEANFILES = paisley

EXTRA_DIST = bash-compgen.in bash-compgen

ENTRY = paisleycmd.command.main.Paisley

paisley: bash-compgen $(top_srcdir)/paisleycmd $(top_srcdir)/paisleycmd/*
	PYTHONPATH=$(top_srcdir):$$PYTHONPATH $(srcdir)/bash-compgen \
		$(completion_DATA) $(ENTRY) > $@
