# version first -- they are parsed LTR and later options depend on automake 1.8
AUTOMAKE_OPTIONS = 1.8 dist-bzip2 no-dist-gzip

ACLOCAL_AMFLAGS = -I m4

SUBDIRS = paisleycmd bin etc m4 misc doc

EXTRA_DIST = paisleycmd.spec README.md RELEASE REVISION


SOURCES = $(top_srcdir)/paisleycmd/*.py $(top_srcdir)/paisleycmd/*/*.py

# pychecker pep8
check:
	@true

pep8:
	for file in $(SOURCES); do $(PYTHON) misc/pep8.py --repeat $$file; done

PYCHECKER_WHITELIST = \
	paisleycmd/*.py \
	paisleycmd/*/*.py

PYCHECKER_BLACKLIST =

release: dist
	make $(PACKAGE)-$(VERSION).tar.bz2.md5

REVISION: $(top_srcdir)/.git paisleycmd/common/common.py
	$(PYTHON) -c 'from paisleycmd.configure import configure; print configure.revision' > REVISION

# generate md5 sum files
%.md5: %
	md5sum $< > $@

include $(top_srcdir)/m4/pychecker.mk

all-local:
	if test -e $(top_srcdir)/.git; then make REVISION; fi
