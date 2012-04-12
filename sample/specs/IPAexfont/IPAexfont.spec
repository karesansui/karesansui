%define _fontdir  %{_datadir}/fonts

Name:           IPAexfont
Version:        1.03
Release:        1%{?dist}
Summary:        IPAex Fonts - JIS X 0213:2004 compliant OpenType fonts

Group:          System Environment/Base 
License:        IPA Font License Agreement v1.0
URL:            http://ossipedia.ipa.go.jp/ipafont/index.html
Vendor:         Karesansui Project
Packager:	Taizo ITO <taizo@karesansui-project.info>
Source0:        IPAexfont00103.zip
Source1:        09-ipaexfont.conf
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

%description
IPAex Fonts - JIS X 0213:2004 compliant OpenType fonts

%prep
%setup -n IPAexfont00103

%build

%install
rm -rf $RPM_BUILD_ROOT

install -dm 755 $RPM_BUILD_ROOT%{_fontdir}/japanese/TrueType/
install -pm 644 ipaexg.ttf $RPM_BUILD_ROOT%{_fontdir}/japanese/TrueType/ipaexg.ttf
install -pm 644 ipaexm.ttf $RPM_BUILD_ROOT%{_fontdir}/japanese/TrueType/ipaexm.ttf

install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.avail/
install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d/
install -pm 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.avail/

%clean
rm -rf $RPM_BUILD_ROOT

%post
ln -s %{_sysconfdir}/fonts/conf.avail/09-ipaexfont.conf %{_sysconfdir}/fonts/conf.d/09-ipaexfont.conf

%postun
rm -f %{_sysconfdir}/fonts/conf.d/09-ipaexfont.conf

%files
%defattr(-,root,root,-)
%doc Readme_IPAexfont00103.txt IPA_Font_License_Agreement_v1.0.txt
%dir %{_fontdir}/japanese/TrueType/
%{_fontdir}/japanese/TrueType/ipaexg.ttf
%{_fontdir}/japanese/TrueType/ipaexm.ttf
%{_sysconfdir}/fonts/conf.avail/*.conf

%changelog
* Tue Mar 13 2012 Taizo ITO <taizo@karesansui-project.info> - 1.03-1
- Initial Package
