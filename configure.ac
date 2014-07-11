dnl initialize autoconf
dnl when going to/from release please remove/add the nano (fourth number)
dnl releases only do Wall, trunk and prerelease does Werror too
AC_INIT(paisleycmd, 0.1.4,
   https://github.com/thomasvs/paisleycmd,
   paisleycmd)

dnl initialize automake
AM_INIT_AUTOMAKE

dnl define PACKAGE_VERSION_* variables
AS_VERSION

AS_NANO

dnl authors
AC_SUBST_FILE(AUTHORS)
AUTHORS=$srcdir/AUTHORS

dnl AM_MAINTAINER_MODE only provides the option to configure to enable it
AM_MAINTAINER_MODE

dnl Add parameters for aclocal
AC_SUBST(ACLOCAL_AMFLAGS, "-I m4")

dnl check for python
AS_PATH_PYTHON(2.3)

dnl check for where to install our python stuff
PYVER=[`$PYTHON -c "import sys ; print sys.version[:3]"`]

dnl This is the best way of installing in an arch-independent location for now
AS_AC_EXPAND(PYTHONLIBDIR, "\${exec_prefix}/lib/python$PYVER/site-packages")

AC_MSG_NOTICE(Installing python code in $PYTHONLIBDIR)
AC_SUBST(PYTHONLIBDIR)

dnl get git revision for installed.py.in
AC_SUBST(REVISION, `$PYTHON -c 'from paisleycmd.configure import configure; print configure.revision'`)
AC_MSG_NOTICE(Setting revision to $REVISION)

dnl check for epydoc
AC_CHECK_PROG(EPYDOC, epydoc, yes, no)
AM_CONDITIONAL(HAVE_EPYDOC, test "x$EPYDOC" = "xyes")

dnl check for pychecker
AC_CHECK_PROG(PYCHECKER, pychecker, yes, no)
AM_CONDITIONAL(HAVE_PYCHECKER, test "x$PYCHECKER" = "xyes")

dnl output stuff
AC_CONFIG_FILES([bin/paisley], [chmod +x bin/paisley])
AC_CONFIG_FILES([etc/bash_completion.d/bash-compgen],
                [chmod +x etc/bash_completion.d/bash-compgen])

AC_OUTPUT(
Makefile
bin/Makefile
doc/Makefile
etc/Makefile
etc/bash_completion.d/Makefile
m4/Makefile
paisleycmd/Makefile
paisleycmd/command/Makefile
paisleycmd/common/Makefile
paisleycmd/configure/Makefile
paisleycmd/configure/uninstalled.py
paisleycmd/configure/installed.py
paisleycmd/extern/Makefile
misc/Makefile
paisleycmd.spec
)
