PYTHON_FILES = clui_constants.py \
ClusterNode.py	\
ClusterNodes.py \
Cluster.py	\
Cman.py		\
ConfigTabController.py  \
ConfigTab.py  \
Device.py \
Dlm.py \
FaildomController.py \
FailoverDomainNode.py \
FailoverDomain.py \
FailoverDomains.py \
FenceDevice.py \
FenceDevices.py \
FenceHandler.py \
Fence.py \
Fs.py \
Group.py \
Ip.py \
MessageLibrary.py \
Method.py \
ModelBuilder.py \
NFSClient.py \
NFSExport.py \
PropertiesRenderer.py \
ResourceGroup.py \
ResourceHandler.py \
Resources.py \
Rm.py \
Script.py \
TagObject.py \
ValidationError.py \
pixmaps/node.png	\
pixmaps/fence.png	\
system-config-cluster.py

GLADE_FILES = clui.glade fence.glade resources.glade

EXTRA_DIST = $(PYTHON_FILES) $(GLADE_FILES)

execdir = $(sbindir)

all-local: 
	rm -f system-config-cluster
	ln -s system-config-cluster.py system-config-cluster

gladedir = $(pkgdatadir)
glade_DATA = $(GLADE_FILES)

install-exec-local:
	mkdir -p $(DESTDIR)$(sbindir) $(DESTDIR)$(bindir) $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(pkgdatadir)/pixmaps/
	sed -e 's/\@VERSION\@/@VERSION@/g' $(srcdir)/system-config-cluster.py > $(DESTDIR)$(pkgdatadir)/system-config-cluster.py
	chmod 755 $(DESTDIR)$(pkgdatadir)/system-config-cluster.py
	install -m 0640 $(srcdir)/clui_constants.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/ClusterNode.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/ClusterNodes.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Cluster.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Cman.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/ConfigTabController.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/ConfigTab.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Device.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Dlm.py $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/FaildomController.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/FailoverDomainNode.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/FailoverDomain.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/FailoverDomains.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/FenceDevice.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/FenceDevices.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/FenceHandler.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Fence.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Fs.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Group.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Ip.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/PropertiesRenderer.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/MessageLibrary.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Method.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/ModelBuilder.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/NFSClient.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/NFSExport.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/ResourceGroup.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/ResourceHandler.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Resources.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Rm.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/Script.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/TagObject.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/ValidationError.py  $(DESTDIR)$(pkgdatadir)/
	install -m 0640 $(srcdir)/pixmaps/fence.png  $(DESTDIR)$(pkgdatadir)/pixmaps/
	install -m 0640 $(srcdir)/pixmaps/node.png  $(DESTDIR)$(pkgdatadir)/pixmaps/
	softdir=$(pkgdatadir); \
	p=$(DESTDIR) ; \
	softdir=$${softdir/#$$p} ; \
	p=$(prefix) ; \
	softdir=$${softdir/#$$p} ; \
	softdir=$${softdir/#\/} ; \
	ln  -fs ../$${softdir}/system-config-cluster.py $(DESTDIR)$(sbindir)/system-config-cluster;

uninstall-local:
	rm -fr $(DESTDIR)$(pkgdatadir)
	rm -f  $(DESTDIR)$(sbindir)/system-config-cluster

docs:
	cd $(srcdir)
	python @PYDOC@ -w $(PYTHON_FILES)
	mv *.html doc

pycheck:
	pychecker -F $(top_srcdir)/pycheckrc $(PYTHON_FILES)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
