Name:           obit
Version:        22JUN10j
Release:        1%{?dist}
Summary:        Obit for ParselTongue
License:        GPLv2+
URL:            http://www.cv.nrao.edu/~bcotton/Obit.html
Source0:        http://www.jive.nl/parseltongue/releases/Obit-%{version}.tar.gz
BuildRequires:  python-devel
BuildRequires:  glib2-devel
BuildRequires:  gsl-devel
%if 0%{?fedora} > 0
BuildRequires:  cfitsio-devel
%endif

%description
Obit for ParselTongue is a stripped-down version of Obit that provides
the functionality needed by ParselTongue.

%prep
%setup -q -n Obit

%build
%configure
make


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_libdir}/%{name}/python
cp -p python/*.py %{buildroot}%{_libdir}/%{name}/python
cp -p python/*.so %{buildroot}%{_libdir}/%{name}/python


%files
%doc
%{_libdir}/*



%changelog
* Thu Jun 25 2015 Mark Kettenis <kettenis@jive.nl> 22JUN10j-1
- Update to Obit 22JUN10j
* Mon Mar  9 2015 Mark Kettenis <kettenis@jive.nl> 22JUN10i-1
- Initial release
