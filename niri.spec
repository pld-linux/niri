Summary:	A scrollable-tiling Wayland compositor
Name:		niri
Version:	25.02
Release:	1
License:	GPL v3
Group:		Applications
Source0:	https://github.com/YaLTeR/niri/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	7557b861a3db42b24e5a064d72670dd3
Source1:	%{name}-crates-%{version}.tar.xz
# Source1-md5:	b329cdc38325178884be9e97f4a8d212
URL:		https://github.com/YaLTeR/niri
BuildRequires:	Mesa-libgbm-devel
BuildRequires:	cairo-devel
BuildRequires:	cairo-gobject-devel
BuildRequires:	cargo
BuildRequires:	clang
%ifnarch x32
BuildRequires:	clang-devel
%else
BuildRequires:	clang-devel(x86-64)
%endif
BuildRequires:	libdisplay-info-devel >= 0.2
BuildRequires:	libinput-devel >= 1.21.0
BuildRequires:	libseat-devel
BuildRequires:	pango-devel
BuildRequires:	pipewire-devel >= 0.3.33
BuildRequires:	pixman-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 2.004
BuildRequires:	rust >= 1.80.1
BuildRequires:	tar >= 1:1.22
BuildRequires:	udev-devel
BuildRequires:	xorg-lib-libxkbcommon-devel
BuildRequires:	xz
Requires:	libinput >= 1.21.0
Requires:	pipewire-libs >= 0.3.33
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_enable_debug_packages	0

%define		filterout_c	-fvar-tracking-assignments

%description
niri is a scrollable-tiling Wayland compositor. Windows are arranged
in columns on an infinite strip going to the right. Opening a new
window never causes existing windows to resize.

Every monitor has its own separate window strip. Windows can never
"overflow" onto an adjacent monitor.

Workspaces are dynamic and arranged vertically. Every monitor has an
independent set of workspaces, and there's always one empty workspace
present all the way down.

%prep
%setup -q -a1

%{__mv} %{name}-%{version}/* .

export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config.toml <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source."git+https://github.com/Smithay/smithay.git"]
git = "https://github.com/Smithay/smithay.git"
replace-with = "vendored-sources"

[source."git+https://gitlab.freedesktop.org/pipewire/pipewire-rs.git"]
git = "https://gitlab.freedesktop.org/pipewire/pipewire-rs.git"
replace-with = "vendored-sources"

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"
export BINDGEN_EXTRA_CLANG_ARGS="%{rpmcflags} %{rpmcppflags}"
%ifnarch x32
export LIBCLANG_PATH="%{_libdir}"
%else
export LIBCLANG_PATH=/usr/lib64
%endif

%cargo_build --frozen

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"
export BINDGEN_EXTRA_CLANG_ARGS="%{rpmcflags} %{rpmcppflags}"
%ifnarch x32
export LIBCLANG_PATH="%{_libdir}"
%else
export LIBCLANG_PATH=/usr/lib64
%endif

install -d $RPM_BUILD_ROOT{%{_bindir},%{_datadir}/wayland-sessions,%{_datadir}/xdg-desktop-portal,%{systemduserunitdir}}

%cargo_install --frozen --root $RPM_BUILD_ROOT%{_prefix} --path $PWD

cp -p resources/niri.desktop $RPM_BUILD_ROOT%{_datadir}/wayland-sessions
cp -p resources/niri-portals.conf $RPM_BUILD_ROOT%{_datadir}/xdg-desktop-portal
cp -p resources/niri-session $RPM_BUILD_ROOT%{_bindir}
cp -p resources/{niri.service,niri-shutdown.target} $RPM_BUILD_ROOT%{systemduserunitdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md resources/default-config.kdl
%attr(755,root,root) %{_bindir}/niri
%attr(755,root,root) %{_bindir}/niri-session
%{_datadir}/wayland-sessions/niri.desktop
%{_datadir}/xdg-desktop-portal/niri-portals.conf
%{systemduserunitdir}/niri.service
%{systemduserunitdir}/niri-shutdown.target
