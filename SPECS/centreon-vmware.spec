# Supported targets: el9

%define install_base /opt/centreon-vmware
%define vmware_modules_howto %(cat <<EOF
Perl modules from VMware vSphere and VMware vsan SDKs must be installed
on the system for this software to work.
The SDKs can be downloaded from Broadcom website:
- https://developer.broadcom.com/sdks/vsphere-perl-sdk/latest
- https://developer.broadcom.com/sdks/vsan-management-sdk-for-perl/latest
An helper script is provided to install the modules, eg:
%{install_base}/share/install-vmware-perl-modules \\\\
    --vsphere /tmp/VMware-vSphere-Perl-SDK-7.0.0-17698549.x86_64.tar.gz \\\\
    --vsan /tmp/vsan-sdk-perl-8.0U3.zip
EOF)

Name: centreon-vmware
Version: 20251200
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
Source4: install-vmware-perl-modules
Patch0: centreon-vmware-packager-deps.patch
Patch1: centreon-vmware-service.patch
Patch2: centreon-vmware-no-vault.patch

BuildArch: noarch

BuildRequires: findutils
BuildRequires: systemd

Requires: centreon-plugins
Requires: perl-XML-LibXML
Requires: perl-Text-Template
Requires: perl-Sys-Syslog

# install-vmware-perl-modules helper script requires the patch command
Requires: patch

%description
Centreon VMWare connector to check ESX server, VCenter and VMWare
guest resources.

%{vmware_modules_howto}

%prep
# centreon-vmware
%setup -c
cd centreon-plugins-plugins-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
cd ..

%install
# centreon-vmware
cd centreon-plugins-plugins-%{version}/connectors/vmware
install -d -m 0755 %{buildroot}/%{install_base}/{bin,share}
install -p -m 0755 src/centreon_vmware.pl %{buildroot}%{install_base}/bin/
find src/centreon/ -type f |while read -r; do
    install -Dp -m 0644 "$REPLY" "%{buildroot}/%{install_base}/lib/perl5/${REPLY#src/}"
done
mv %{buildroot}/%{install_base}/lib/perl5/centreon/script/centreon_vmware_convert_config_file \
    %{buildroot}/%{install_base}/share/
chmod 0755 %{buildroot}/%{install_base}/share/centreon_vmware_convert_config_file
install -Dp -m 0644 packaging/config/centreon_vmware-conf.pm \
    %{buildroot}/%{install_base}/share/centreon_vmware-conf.pm.sample
install -d -m 0755 %{buildroot}/%{_sysconfdir}
install -d -m 0700 %{buildroot}/%{_sysconfdir}/centreon
install -Dp -m 0600 %{SOURCE1} %{buildroot}/%{_sysconfdir}/centreon/centreon_vmware.pm
install -Dp -m 0644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/centreon_vmware
install -Dp -m 0644 %{SOURCE3} %{buildroot}/%{_sysconfdir}/logrotate.d/centreon_vmware
install -Dp -m 0755 -t %{buildroot}/%{install_base}/share/ %{SOURCE4}
install -Dp -m 0644 packaging/redhat/centreon_vmware-systemd %{buildroot}/%{_unitdir}/centreon_vmware.service
install -d -m 0700 %{buildroot}/%{_localstatedir}/log/centreon
cd ../../..

%pre
if ! getent group centreon >/dev/null; then
    groupadd -r centreon
fi
if ! getent passwd centreon >/dev/null; then
    useradd -r -g centreon -d %{_localstatedir}/log/centreon -s /sbin/nologin centreon
fi

%post
%systemd_post centreon_vmware.service
echo '%{vmware_modules_howto}' |sed -re 's,^,%{name}: ,'

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
%{install_base}
%attr(-, centreon, centreon) %dir %{_localstatedir}/log/centreon
