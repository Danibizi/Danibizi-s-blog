---
title: Compilación de un programa en C utilizando un Makefile.
date: 2026-09-30T14:19:00
draft: false
description: Compilación de un programa en C utilizando un Makefile,usando para el ejemplo el paquete lynx para debian.
cover:
  image: /img/a_clean_modern_minimalist_tech_themed_banner_pos.png
  alt: ''
tags:
  - '2ASIR'
  - 'ASO'
---

Para esta tarea compilare el progama lynx,el cual esta escrito en C,para ello descargare su repositorio oficial el cual es:

[https://invisible-island.net/archives/lynx/tarballs/lynx2.9.3.tar.gz](https://invisible-island.net/archives/lynx/tarballs/lynx2.9.3.tar.gz)

Al descomprimir:

\`\`\`

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ ls

ABOUT-NLS    build.com     configure       descrip.mms   LYHelp.hin       makefile.bcb  PACKAGE   scripts

aclocal.m4   CHANGES       configure.in    docs          LYMessages_en.h  makefile.in   plink.sh  src

AUTHORS      clean.com     COPYHEADER      fixed512.com  lynx.cfg         makefile.msc  po        test

bcblibs.bat  config.guess  COPYHEADER.asc  INSTALLATION  lynx_help        makelynx.bat   PROBLEMS  userdefs.h

BUILD        config.hin    COPYING         install-sh    lynx.hlp         make-msc.bat   README    VMSPrint.com

build.bat    config.sub     COPYING.asc     lib           lynx.man         makew32.bat   samples   WWW

\`\`\`

Como vemos tenemos el fichero configure y el fichero makefile.in que el configure convertiran en makefile.

\`\`\`

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ ls src/

AttrList.h      HTNestedList.h  LYDownload.c    LYHistory.h   LYMap.c        LYSession.c    makefile.dos       tidy_tls.c

chrtrans        HTSaveToFile.h  LYDownload.h    LYIcon.rc     LYMap.h        LYSession.h    makefile.dsl       TRSTable.c

cmu_tcp.opt     LYBookmark.c    LYebcdic.c      LYJump.c      LYmktime.c     LYShowInfo.c   makefile.in        TRSTable.h

decc.opt        LYBookmark.h    LYEdit.c        LYJump.h      LYNews.c       LYShowInfo.h   makefile.wsl        UCAuto.c

DefaultStyle.c  LYCgi.c         LYEdit.h        LYJustify.h   LYNews.h       LYSignal.h     mktime.c           UCAuto.h

descrip.mms     LYCgi.h        LYEditmap.c     LYKeymap.c    LYOptions.c    LYStrings.c    multinet.opt       UCAux.c

gnuc.opt        LYCharSets.c    LYexit.c        LYKeymap.h    LYOptions.h    LYStrings.h    multinet_ucx.opt   UCdomap.c

GridText.c      LYCharSets.h   LYExtern.c      LYLeaks.c     LYPrettySrc.c  LYStructs.h    parsdate.c          UCdomap.h

GridText.h      LYCharUtils.c  LYExtern.h      LYList.c      LYPrettySrc.h   LYStyle.c      parsdate.h           ucxolb.opt

HTAlert.c        LYCharUtils.h  LYForms.c       LYList.h      LYPrint.c      LYTraversal.c  socketshr_tcp.opt    win_tcp.opt

HTFont.h        LYClean.c      LYGetFile.c     LYLocal.h     LYrcFile.c      LYTraversal.h  strstr.c             wcwidth.c

HTForms.h        LYClean.h      LYGetFile.h    LYMail.c      LYrcFile.h      LYUpload.c     structdump.h          wcwidth.h

HTFWriter.c      LYCookie.c     LYGlobalDefs.h LYMail.h      LYReadCFG.c     LYUpload.h     tcpipolb.opt          Xsystem.c

HTInit.c         LYCookie.h     LYHash.c        LYMain.c      LYReadCFG.h     LYUtils.c      tcpipshr.opt

HTML.c           LYCurses.c     LYHash.h        LYMainLoop.c  LYSearch.c      LYUtils.h      tcpwareolb.opt

HTML.h           LYCurses.h     LYHistory.c     LYMainLoop.h  LYSearch.h      LYVMSdef.h     tcpwareshr.opt

\`\`\`

Podemos ver que esta escrito en C,antes que nada vamos a descargar las dependecias,en caso de tenerlas para que no falle nada:

\`\`\`

sudo apt build-dep lynx

\`\`\`

Podemos proceder con el configure:

\`\`\`

./configure --prefix=/opt/lynx-2.9.3

\`\`\`

Una vez hecho el configure podemos ver que aparece el makefile:

\`\`\`

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ ls

ABOUT-NLS    cfg_defs.h    config.status   COPYING.asc     lib              lynx.hlp      make-msc.bat  README        WWW

aclocal.m4   CHANGES       config.sub      descrip.mms     LYHelp.h         lynx.man      makew32.bat   samples

AUTHORS      clean.com     configure       docs            LYHelp.hin       makefile      man2html.tmp  scripts

bcblibs.bat  config.cache  configure.in    fixed512.com    LYMessages_en.h  makefile.bcb  PACKAGE       src

BUILD        config.guess  COPYHEADER      help_files.sed  lynx.cfg         makefile.in   plink.sh      test

build.bat    config.hin    COPYHEADER.asc  INSTALLATION    lynx_cfg.h       makefile.msc  po            userdefs.h

build.com    config.log    COPYING         install-sh      lynx_help        makelynx.bat   PROBLEMS      VMSPrint.com

\`\`\`

Ahora para compilar tendremos que tener instalado make y el compilador GCC

\`\`\`

sudo apt install make

sudo apt install build-essential

\`\`\`

Una vez hecho el comando make,si todo ha salido bien podemos proceder el make install:

\`\`\`

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ sudo make install

mkdir -p /opt/lynx-2.9.3/bin

/bin/sh -c "P=\`echo lynx|sed 's,x,x,'\`; \

if test -f /opt/lynx-2.9.3/bin/$P ; then \

      mv -f /opt/lynx-2.9.3/bin/$P /opt/lynx-2.9.3/bin/$P.old; fi"; \

/usr/bin/install -c lynx /opt/lynx-2.9.3/bin/\`echo lynx|sed 's,x,x,'\`

mkdir -p /opt/lynx-2.9.3/share/man/man1

/usr/bin/install -c -m 644 ./lynx.man /opt/lynx-2.9.3/share/man/man1/\`echo lynx|sed 's,x,x,'\`.1

mkdir -p /opt/lynx-2.9.3/etc

\*\* installing ./lynx.cfg as /opt/lynx-2.9.3/etc/lynx.cfg

\*\* installing ./samples/lynx.lss as /opt/lynx-2.9.3/etc/lynx.lss

Use make install-help to install the help-files

Use make install-doc to install extra documentation files

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ ls /opt/

lynx-2.9.3

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ ls /opt/lynx-2.9.3/

bin  etc  share

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ ls /opt/lynx-2.9.3/bin/

lynx

\`\`\`

Y si ejecutamos el binario:

\`\`\`

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ sudo /opt/lynx-2.9.3/bin/lynx google.com

\`\`\`

\`\`\`

                                                                                                                                Google

   Mettez M-\` jour votre navigateur

   Votre navigateur n'est plus pris en charge. Pour poursuivre votre recherche, passez M-\` une version rM-icenEn savoir plusplus

Commands: Use arrow keys to move, '?' for help, 'q' to quit, '<-' to go back.

  Arrow keys: Up and Down to move.  Right to follow a link; Left to go back.

 H)elp O)ptions P)rint G)o M)ain screen Q)uit /=search [delete]=history list

\`\`\`

Como vemos ya lo tenemos instalado con exito,y si miramos lo tenemos sin usar paqueteria:

\`\`\`

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ apt policy lynx

lynx:

  Instalados: (ninguno)

  Candidato:  2.9.2-1

  Tabla de versión:

     2.9.2-1 500

        500 http://deb.debian.org/debian trixie/main amd64 Packages

\`\`\`

Como vemos debian ofrece la 2.9.2-1 y gracias a compilarlo,tenemos la 2.9.3,por tanto teniendo las funcionnalidades o mejoras que contenga esta version.

Podemos ver estos cambios en:

[https://lynx.invisible-island.net/current/CHANGES.html#v2.8.1dev.1](https://lynx.invisible-island.net/current/CHANGES.html#v2.8.1dev.1)

\`\`\`

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ cat makefile | grep uninstall

uninstall ::

# ( cd $(PO_DIR) && $(MAKE_RECUR) uninstall )

uninstall \

uninstall-help ::

uninstall \

uninstall-doc ::

\`\`\`

Como vemos en el makefile si hay uninstall entonces para desinstalarlo basta con hacer un make uninstall,y borrar  a mano el fichero donde hizimos el wget y el fichero del /opt ya que el uninstall lo que hace es borrar el binario y los archivos asociados a este,pero no donde tenemos el codigo fuente y tampoco las carpetas que contenian el binario

\`\`\`

sudo make uninstall

rm -f /opt/lynx-2.9.3/bin/\`echo lynx|sed 's,x,x,'\` ;\

rm -f /opt/lynx-2.9.3/share/man/man1/\`echo lynx|sed 's,x,x,'\`.1 ;\

rm -f /opt/lynx-2.9.3/etc/lynx.cfg ;\

rm -f /opt/lynx-2.9.3/etc/lynx.lss

/bin/sh -c 'if test -d "/opt/lynx-2.9.3/share/lynx_help" ; then \

	WD=\`cd "/opt/lynx-2.9.3/share/lynx_help" && pwd\` ; \

	TAIL=\`basename "/opt/lynx-2.9.3/share/lynx_help"\` ; \

	HEAD=\`echo "$WD"|sed -e "s,/${TAIL}$,,"\` ; \

	test "x$WD" != "x$HEAD" && rm -rf "/opt/lynx-2.9.3/share/lynx_help"; \

	fi'

/bin/sh -c 'if test -d "/opt/lynx-2.9.3/share/lynx_doc" ; then \

	WD=\`cd "/opt/lynx-2.9.3/share/lynx_doc" && pwd\` ; \

	TAIL=\`basename "/opt/lynx-2.9.3/share/lynx_doc"\` ; \

	HEAD=\`echo "$WD"|sed -e "s,/${TAIL}$,,"\` ; \

	test "x$WD" != "x$HEAD" && rm -rf "/opt/lynx-2.9.3/share/lynx_doc"; \

	fi' ;\

 /bin/sh -c 'if test -d "/opt/lynx-2.9.3/share/lynx_help" ; then \

	WD=\`cd "/opt/lynx-2.9.3/share/lynx_help" && pwd\` ; \

	TAIL=\`basename "/opt/lynx-2.9.3/share/lynx_help"\` ; \

	HEAD=\`echo "$WD"|sed -e "s,/'${TAIL}'$,,"\` ; \

	test "x$WD" != "x$HEAD" ; \

	cd "/opt/lynx-2.9.3/share/lynx_help" && rm -f COPYING COPYHEADER ; \

	fi'

\`\`\`

\`\`\`

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ sudo rm -rf /opt/lynx-2.9.3/

usuario@debianprinter:/tmp/lynx/lynx2.9.3$ sudo rm -rf ../../lynx/

\`\`\`
