# Supported targets: el9

%define install_base /opt/centreon-vmware
%define packager_deps %{install_base}/_packager_deps

Name: centreon-vmware
Version: 20250700
Release: 1%{?dist}.zenetys
Summary: Centreon VMWare connector
Group: Applications/System
License: ASL 2.0
URL: https://github.com/centreon/centreon-plugins/tree/master/connectors/vmware

# centreon-vmware
Source0: https://github.com/centreon/centreon-plugins/archive/refs/tags/plugins-%{version}.tar.gz
Source1: centreon_vmware-conf.pm
Source2: centreon_vmware-sysconfig
Source3: centreon_vmware-logrotate
Patch0: centreon-vmware-packager-deps.patch
Patch1: centreon-vmware-service.patch
Patch2: centreon-vmware-vsan-path.patch
Patch3: centreon-vmware-no-vault.patch

# bundled dependencies
# Download VMware SDK and put the files in the SOURCES/ directory:
# https://developer.broadcom.com/sdks/vsphere-perl-sdk/latest
# https://developer.broadcom.com/sdks/vsan-management-sdk-for-perl/latest
Source100: VMware-vSphere-Perl-SDK-7.0.0-17698549.x86_64.tar.gz
Source101: vsan-sdk-perl.zip#/vsan-sdk-perl-8.0U3.zip

BuildArch: noarch

BuildRequires: findutils
BuildRequires: systemd

Requires: centreon-plugins
Requires: perl-XML-LibXML
Requires: perl-Text-Template
Requires: perl-Sys-Syslog

%description
Centreon VMWare connector to check ESX server, VCenter
and VMWare guest resources.

Bundled dependencies:
- perl modules from VMware-vSphere-Perl-SDK
- perl modules from vsan-sdk-perl

%prep
# centreon-vmware
%setup -c
cd centreon-plugins-plugins-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
cd ..

# VMware-vSphere-Perl-SDK
%setup -T -D -a 100

# vsan-sdk-perl
%setup -T -D -a 101

%install
# centreon-vmware
cd centreon-plugins-plugins-%{version}/connectors/vmware
install -d -m 0755 %{buildroot}/%{install_base}/{bin,share}
install -p -m 0755 src/centreon_vmware.pl %{buildroot}%{install_base}/bin/
find src/centreon/ -type f -exec \
    sh -c 'install -Dp -m 0644 "$1" "%{buildroot}/%{install_base}/lib/perl5/${1#src/}"' -- "{}" \;
mv %{buildroot}/%{install_base}/lib/perl5/centreon/script/centreon_vmware_convert_config_file \
    %{buildroot}/%{install_base}/share/
install -Dp -m 0644 packaging/config/centreon_vmware-conf.pm \
    %{buildroot}/%{install_base}/share/centreon_vmware-conf.pm.sample
install -d -m 0755 %{buildroot}/%{_sysconfdir}
install -d -m 0700 %{buildroot}/%{_sysconfdir}/centreon
install -Dp -m 0600 %{SOURCE1} %{buildroot}/%{_sysconfdir}/centreon/centreon_vmware.pm
install -Dp -m 0644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/centreon_vmware
install -Dp -m 0644 %{SOURCE3} %{buildroot}/%{_sysconfdir}/logrotate.d/centreon_vmware
install -Dp -m 0644 packaging/redhat/centreon_vmware-systemd %{buildroot}/%{_unitdir}/centreon_vmware.service
install -d -m 0700 %{buildroot}/%{_localstatedir}/log/centreon
cd ../../..

# VMware-vSphere-Perl-SDK
cd vmware-vsphere-cli-distrib
install -d -m 0755 %{buildroot}/%{packager_deps}/lib/perl5/VMware
find lib/VMware/share/VMware/ -type f -exec \
    install -p -m 0644 {} %{buildroot}/%{packager_deps}/lib/perl5/VMware/ \;
install -p -m 0644 doc/EULA %{buildroot}/%{packager_deps}/lib/perl5/VMware/
install -p -m 0644 doc/README.copyright %{buildroot}/%{packager_deps}/lib/perl5/VMware/
cd ..

# vsan-sdk-perl
cd vsan-sdk-perl
find bindings/ -type f -exec \
    install -p -m 0644 {} %{buildroot}/%{packager_deps}/lib/perl5/VMware/ \;
cd ..

%pre
if ! getent group centreon >/dev/null; then
    groupadd -r centreon
fi
if ! getent passwd centreon >/dev/null; then
    useradd -r -g centreon -d %{_localstatedir}/log/centreon -s /sbin/nologin centreon
fi

%post
%systemd_post centreon_vmware.service

%preun
%systemd_preun centreon_vmware.service

%postun
%systemd_postun_with_restart centreon_vmware.service

%files
%doc centreon-plugins-plugins-%{version}/connectors/vmware/changelog
%doc centreon-plugins-plugins-%{version}/connectors/vmware/README.md
%license centreon-plugins-plugins-%{version}/LICENSE.txt
%attr(-, centreon, centreon) %{_sysconfdir}/centreon
%config(noreplace) %attr(-, centreon, centreon) %{_sysconfdir}/centreon/centreon_vmware.pm
%config(noreplace) %{_sysconfdir}/logrotate.d/centreon_vmware
%config(noreplace) %{_sysconfdir}/sysconfig/centreon_vmware
%{_unitdir}/centreon_vmware.service
/opt/centreon-vmware
%attr(-, centreon, centreon) %dir %{_localstatedir}/log/centreon
