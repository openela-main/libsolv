%global libname solv

%bcond_without python_bindings
%bcond_without perl_bindings
%bcond_without ruby_bindings
# Creates special prefixed pseudo-packages from appdata metadata
%bcond_without appdata
# Creates special prefixed "group:", "category:" pseudo-packages
%bcond_without comps
%bcond_without conda
# For rich dependencies
%bcond_without complex_deps
%bcond_without helix_repo
%bcond_without suse_repo
%bcond_without debian_repo
%bcond_without arch_repo
# For handling deb + rpm at the same time
%bcond_without multi_semantics
%bcond_with zchunk
%bcond_without zstd

%define __cmake_switch(b:) %[%{expand:%%{?with_%{-b*}}} ? "ON" : "OFF"]

Name:           lib%{libname}
Version:        0.7.24
Release:        2%{?dist}
Summary:        Package dependency solver

License:        BSD
URL:            https://github.com/openSUSE/libsolv
Source:         %{url}/archive/%{version}/%{name}-%{version}.tar.gz
# https://bugzilla.redhat.com/show_bug.cgi?id=1993126
Patch1:         0001-Add-support-for-computing-hashes-using-OpenSSL.patch
Patch2:         0002-Revert-Improve-choice-rule-generation.patch
Patch3:         0003-Revert-Add-complex_deps-requirement-to-choice1b-test.patch
Patch4:         0004-Revert-Add-more-choicerules-tests.patch
Patch5:         0005-Treat-condition-both-as-positive-and-negative-litera.patch
Patch6:         0006-Allow_break_arch_lock_step_on_erase.patch

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(rpm)
BuildRequires:  zlib-devel
# -DWITH_LIBXML2=ON
BuildRequires:  libxml2-devel
# -DWITH_OPENSSL=ON
BuildRequires:  pkgconfig(openssl)
# -DENABLE_LZMA_COMPRESSION=ON
BuildRequires:  xz-devel
# -DENABLE_BZIP2_COMPRESSION=ON
BuildRequires:  bzip2-devel
%if %{with zstd}
# -DENABLE_ZSTD_COMPRESSION=ON
BuildRequires:  libzstd-devel
%endif
%if %{with zchunk}
# -DENABLE_ZCHUNK_COMPRESSION=ON
BuildRequires:  pkgconfig(zck)
%endif

%description
A free package dependency solver using a satisfiability algorithm. The
library is based on two major, but independent, blocks:

- Using a dictionary approach to store and retrieve package
  and dependency information.

- Using satisfiability, a well known and researched topic, for
  resolving package dependencies.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       rpm-devel%{?_isa}

%description devel
Development files for %{name}.

%package tools
Summary:        Package dependency solver tools
Requires:       %{name}%{?_isa} = %{version}-%{release}
# repo2solv dependencies. Used as execl()
Requires:       /usr/bin/find

%description tools
Package dependency solver tools.

%package demo
Summary:        Applications demoing the %{name} library
Requires:       %{name}%{?_isa} = %{version}-%{release}
# solv dependencies. Used as execlp() and system()
Requires:       /usr/bin/curl
Requires:       /usr/bin/gpg2

%description demo
Applications demoing the %{name} library.

%if %{with perl_bindings}
%package -n perl-%{libname}
Summary:        Perl bindings for the %{name} library
BuildRequires:  swig
BuildRequires:  perl-devel
BuildRequires:  perl-generators
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n perl-%{libname}
Perl bindings for the %{name} library.
%endif

%if %{with ruby_bindings}
%package -n ruby-%{libname}
Summary:        Ruby bindings for the %{name} library
BuildRequires:  swig
BuildRequires:  ruby-devel
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n ruby-%{libname}
Ruby bindings for the %{name} library.
%endif

%if %{with python_bindings}
%package -n python3-%{libname}
Summary:        Python bindings for the %{name} library
%{?python_provide:%python_provide python3-%{libname}}
BuildRequires:  swig
BuildRequires:  python3-devel
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n python3-%{libname}
Python bindings for the %{name} library.

Python 3 version.
%endif

%prep
%autosetup -p1

%build
%cmake -GNinja                                            \
  -DFEDORA=1                                              \
  -DENABLE_RPMDB=ON                                       \
  -DENABLE_RPMDB_BYRPMHEADER=ON                           \
  -DENABLE_RPMDB_LIBRPM=ON                                \
  -DENABLE_RPMPKG_LIBRPM=ON                               \
  -DENABLE_RPMMD=ON                                       \
  -DENABLE_COMPS=%{__cmake_switch -b comps}               \
  -DENABLE_APPDATA=%{__cmake_switch -b appdata}           \
  -DUSE_VENDORDIRS=ON                                     \
  -DWITH_LIBXML2=ON                                       \
  -DWITH_OPENSSL=ON                                       \
  -DENABLE_LZMA_COMPRESSION=ON                            \
  -DENABLE_BZIP2_COMPRESSION=ON                           \
  -DENABLE_ZSTD_COMPRESSION=%{__cmake_switch -b zstd}     \
  -DENABLE_ZCHUNK_COMPRESSION=%{__cmake_switch -b zchunk} \
%if %{with zchunk}
  -DWITH_SYSTEM_ZCHUNK=ON                                 \
%endif
  -DENABLE_HELIXREPO=%{__cmake_switch -b helix_repo}      \
  -DENABLE_SUSEREPO=%{__cmake_switch -b suse_repo}        \
  -DENABLE_DEBIAN=%{__cmake_switch -b debian_repo}        \
  -DENABLE_ARCHREPO=%{__cmake_switch -b arch_repo}        \
  -DMULTI_SEMANTICS=%{__cmake_switch -b multi_semantics}  \
  -DENABLE_COMPLEX_DEPS=%{__cmake_switch -b complex_deps} \
  -DENABLE_CONDA=%{__cmake_switch -b conda}               \
  -DENABLE_PERL=%{__cmake_switch -b perl_bindings}        \
  -DENABLE_RUBY=%{__cmake_switch -b ruby_bindings}        \
  -DENABLE_PYTHON=%{__cmake_switch -b python_bindings}    \
%if %{with python_bindings}
  -DPYTHON_EXECUTABLE=%{python3}                          \
%endif
  %{nil}
%cmake_build

%install
%cmake_install

%check
%ctest

# Python smoke test (not tested in %%ctest):
export PYTHONPATH=%{buildroot}%{python3_sitearch}
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
%python3 -c 'import solv'

%files
%license LICENSE*
%doc README
%{_libdir}/%{name}.so.*
%{_libdir}/%{name}ext.so.*

%files devel
%{_libdir}/%{name}.so
%{_libdir}/%{name}ext.so
%{_includedir}/%{libname}/
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/pkgconfig/%{name}ext.pc
# Own directory because we don't want to depend on cmake
%dir %{_datadir}/cmake/Modules/
%{_datadir}/cmake/Modules/FindLibSolv.cmake
%{_mandir}/man3/%{name}*.3*

# Some small macro to list tools with mans
%global solv_tool() \
%{_bindir}/%{1}\
%{_mandir}/man1/%{1}.1*

%files tools
%solv_tool deltainfoxml2solv
%solv_tool dumpsolv
%solv_tool installcheck
%solv_tool mergesolv
%solv_tool repomdxml2solv
%solv_tool rpmdb2solv
%solv_tool rpmmd2solv
%solv_tool rpms2solv
%solv_tool testsolv
%solv_tool updateinfoxml2solv
%solv_tool repo2solv
%if %{with comps}
  %solv_tool comps2solv
%endif
%if %{with appdata}
  %solv_tool appdata2solv
%endif
%if %{with debian_repo}
  %solv_tool deb2solv
%endif
%if %{with arch_repo}
  %solv_tool archpkgs2solv
  %solv_tool archrepo2solv
%endif
%if %{with helix_repo}
  %solv_tool helix2solv
%endif
%if %{with suse_repo}
  %solv_tool susetags2solv
%endif
%if %{with conda}
  %{_bindir}/conda2solv
%endif

%files demo
%solv_tool solv

%if %{with perl_bindings}
%files -n perl-%{libname}
%{perl_vendorarch}/%{libname}.pm
%{perl_vendorarch}/%{libname}.so
%endif

%if %{with ruby_bindings}
%files -n ruby-%{libname}
%{ruby_vendorarchdir}/%{libname}.so
%endif

%if %{with python_bindings}
%files -n python3-%{libname}
%{python3_sitearch}/_%{libname}.so
%{python3_sitearch}/%{libname}.py
%{python3_sitearch}/__pycache__/%{libname}.*
%endif

%changelog
* Wed Jun 21 2023 Jaroslav Rohel <jrohel@redhat.com> - 0.7.24-2
- Backport Allow to break arch lock-step on erase operations (RhBug:2172288,2172292)

* Tue May 16 2023 Jaroslav Rohel <jrohel@redhat.com> - 0.7.24-1
- Update to 0.7.24
- Backport Treat condition both as positive and negative literal in pool_add_pos_literals_complex_dep
  (RhBug:2185061,2190136)

* Thu Dec 15 2022 Nicola Sella <nsella@redhat.com> - 0.7.22-4
- Delete patch "Move OpenSSL functions" to fix ABI change

* Wed Dec 07 2022 Nicola Sella <nsella@redhat.com> - 0.7.22-3
- Revert choice rule generation to fix pick of old build (RhBug:2150300,RhBug:2151551)

* Mon Oct 31 2022 Nicola Sella <nsella@redhat.com> - 0.7.22-2
- Move OpenSSL functions to use 3.0 compatible API

* Thu Apr 28 2022 Pavla Kratochvilova <pkratoch@redhat.com> - 0.7.22-1
- Update to 0.7.22
- support strict repository priorities new solver flag: SOLVER_FLAG_STRICT_REPO_PRIORITY
- support zstd compressed control files in debian packages
- add an ifdef allowing to rename Solvable dependency members ("requires" is a keyword in C++20)
- support setting/reading userdata in solv files new functions: repowriter_set_userdata, solv_read_userdata
- support queying of the custom vendor check function new function: pool_get_custom_vendorcheck
- support solv files with an idarray block
- allow accessing the toolversion at runtime
- support parsing of Debian's Multi-Arch indicator
- fix segfault on conflict resolution when using bindings
- fix split provides not working if the update includes a forbidden vendor change
- reworked choice rule generation to cover more usecases
- support SOLVABLE_PREREQ_IGNOREINST in the ordering code

* Wed Nov 10 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.7.20-2
- Build without support of zchunk (RhBug:2021084)

* Mon Oct 25 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.7.20-1
- Update to 0.7.20
- new SOLVER_EXCLUDEFROMWEAK job to ignore pkgs for weak dependencies
- support for environments in comps parser
- fix misparsing of '&' in attributes with libxml2
- choice rules: treat orphaned packages as newest
- fix compatibility with Python 3.10

* Thu Aug 12 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.7.19-3
- Use OpenSSL for computing hashes (RhBug:1993126)

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 0.7.19-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jul 27 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.7.19-1
- Update to 0.7.19
- repo_add_conda: add flag to skip v2 packages
- fix rare segfault in resolve_jobrules() that could happen if new rules are learnt
- fix memory leaks

* Tue Jul 27 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.7.17-6
- Fix issues detected by static analyzers

* Tue Jun 22 2021 Mohan Boddu <mboddu@redhat.com> - 0.7.17-5
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 0.7.17-4
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.7.17-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sat Jan 23 2021 Igor Raits <ignatenkobrain@fedoraproject.org> - 0.7.17-2
- Drop unneeded explicit dependency on RPM

* Thu Jan 21 2021 Igor Raits <ignatenkobrain@fedoraproject.org> - 0.7.17-1
- Update to 0.7.17

* Thu Jan  7 2021 Vít Ondruch <vondruch@redhat.com> - 0.7.15-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_3.0

* Mon Nov 16 2020 Miro Hrončok <mhroncok@redhat.com> - 0.7.15-2
- Backport upstream fix for Python 3.10 compatibility
- Fixes: rhbz#1896411

* Mon Oct 19 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 0.7.15-1
- Update to 0.7.15

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.7.14-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 03 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 0.7.14-3
- Switch to %%cmake_build/%%cmake_install
- Drop Python 2 bindings

* Wed Jun 03 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 0.7.14-2
- Raise lowest compatible RPM version

* Wed May 27 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 0.7.14-1
- Update to 0.7.14

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 0.7.12-4
- Rebuilt for Python 3.9

* Mon May 25 2020 Colin Walters <walters@verbum.org> - 0.7.12-3
- Apply https://github.com/openSUSE/libsolv/pull/386
  to fix https://bugzilla.redhat.com/show_bug.cgi?id=1838691

* Mon May 25 2020 Miro Hrončok <mhroncok@redhat.com> - 0.7.12-2
- Rebuilt for Python 3.9

* Tue Apr 21 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 0.7.12-1
- Update to 0.7.12

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.7.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jan 23 05:17:39 EST 2020 Neal Gompa <ngompa13@gmail.com> - 0.7.11-1
- Update to 0.7.11

* Tue Dec 17 08:41:00 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.10-1
- Update to 0.7.10

* Tue Nov 12 12:52:58 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.8-1
- Update to 0.7.8

* Sat Oct 19 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.7-1
- Update to 0.7.7

* Mon Oct 14 2019 Jaroslav Mracek <jmracek@redhat.com> - 0.7.6-3
- Backport support of POOL_FLAG_WHATPROVIDESWITHDISABLED pool flag

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 0.7.6-2
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Fri Aug 30 09:08:03 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.6-1
- Update to 0.7.6

* Sun Aug 18 2019 Miro Hrončok <mhroncok@redhat.com> - 0.7.5-4
- Rebuilt for Python 3.8

* Sun Aug 04 11:07:46 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.5-3
- Fix queries with src.rpm with DynamicBuildRequires

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.7.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jun 12 15:58:49 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.5-1
- Update to 0.7.5

* Mon Jun 10 22:13:20 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.4-5
- Rebuild for RPM 4.15

* Mon Jun 10 15:42:03 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.4-4
- Rebuild for RPM 4.15

* Tue May 21 2019 Jitka Plesnikova <jplesnik@redhat.com> - 0.7.4-3
- Fixed build for SWIG 4.0.0 (#1707367)

* Tue Apr 02 14:45:22 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.4-2
- Backport patch to fix solver_solve() running multiple times with SOLVER_FAVOR

* Fri Mar 29 16:13:00 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.4-1
- Update to 0.7.4

* Tue Feb 26 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.7.3-4
- Backport: Add support for modular updateinfo.xml data

* Wed Feb 13 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.3-3
- bindings: Add best_solvables/whatmatchessolvable

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.7.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Jan 30 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.3-1
- Update to 0.7.3

* Tue Jan 15 2019 Jaroslav Mracek <jmracek@redhat.com> - 0.7.2-2
- Backport Do-not-disable-infarch-rules-when-they-dont-conflict-with-the-job

* Sat Jan 12 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.2-2
- Fix small security issues

* Mon Dec 10 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.2-1
- Update to 0.7.2

* Fri Nov 30 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org - 0.7.1-2
- Backport fixes for autouninstall

* Wed Oct 31 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.1-1
- Update to 0.7.1

* Sun Oct 28 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.7.0-1
- Update to 0.7.0

* Mon Oct 01 2018 Jaroslav Rohel <jrohel@redhat.org> - 0.6.35-3
- Backport patch: Make sure that targeted updates don't do reinstalls

* Mon Oct 01 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.35-2
- Disable python2 subpackage

* Thu Aug 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.35-1
- Update to 0.6.35

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.34-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 02 2018 Miro Hrončok <mhroncok@redhat.com> - 0.6.34-5
- Rebuilt for Python 3.7

* Mon Jul 02 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.34-4
- Rebuilt for Python 3.7

* Fri Jun 29 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.34-3
- Backport few fixes and enhancements from upstream

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.6.34-2
- Rebuilt for Python 3.7

* Mon Mar 26 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.34-1
- Update to 0.6.34

* Wed Feb 28 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.33-1
- Update to 0.6.33

* Tue Feb 13 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.32-1
- Update to 0.6.32

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.31-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 31 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.31-1
- Update to 0.6.31

* Tue Jan 30 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-9.git.2901.47fbaa2
- Use librpm to access rpm headers

* Tue Jan 30 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-8.git.2900.8bdcce1
- Use librpm to access DB

* Tue Jan 30 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-7.git.2898.ae214a6
- Switch to %%ldconfig_scriptlets

* Mon Jan 29 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-6.git.2898.ae214a6
- Disable librpm from accessing DB

* Mon Jan 29 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-5.git.2898.ae214a6
- Allow disabling python2 bindings

* Mon Jan 29 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-4.git.2898.ae214a6
- Switch to ninja-build

* Mon Jan 29 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-3.git.2898.ae214a6
- Update to latest git version
- Switch to use librpm for accessing headers / rpmdb

* Mon Nov 20 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-3.git.2887.97b8c0c
- Update to latest snapshot

* Mon Nov 06 2017 Panu Matilainen <pmatilai@redhat.com> - 0.6.30-2
- Better error message on DB_VERSION_MISMATCH errors

* Tue Oct 24 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.30-1
- Update to 0.6.30

* Tue Sep 19 2017 Panu Matilainen <pmatilai@redhat.com> - 0.6.29-2
- Band-aid for DB_VERSION_MISMATCH errors on glibc updates

* Thu Sep 07 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.29-1
- Update to 0.6.29

* Fri Aug 11 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.6.28-8
- Rebuilt after RPM update (№ 3)

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.6.28-7
- Rebuilt for RPM soname bump

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.6.28-6
- Rebuilt for RPM soname bump

* Thu Aug 03 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.28-5
- Add support for REL_WITHOUT

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.28-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.28-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 21 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.28-2
- Backport patch for fixing yumobs

* Sat Jul 01 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.28-1
- Update to 0.6.28

* Mon May 29 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.27-2
- Backport few fixes for bindings

* Thu May 04 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.27-1
- Update to 0.6.27

* Mon Mar 27 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.26-5.git.20.668e249
- Update to latest snapshot

* Sat Mar 18 2017 Neal Gompa <ngompa13@gmail.com> - 0.6.26-4.git.19.2262346
- Enable AppData support (#1427171)

* Thu Mar 16 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.26-3.git.19.2262346
- Update to latest git
- Switch to libxml2

* Mon Mar 06 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.26-2
- Use %%{__python3} as PYTHON3_EXECUTABLE

* Wed Feb 15 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.26-1
- Update to 0.6.26

* Tue Feb 07 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.6.25-1
- Update to 0.6.25

* Fri Jan 13 2017 Vít Ondruch <vondruch@redhat.com> - 0.6.24-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.4

* Mon Dec 12 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.6.24-3
- Rebuild for Python 3.6

* Fri Dec 09 2016 Orion Poplawski <orion@cora.nwra.com> - 0.6.24-2
- Use upstream python build options

* Fri Nov 11 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.24-1
- Update to 0.6.24

* Sat Oct 29 2016 Denis Ollier <larchunix@gmail.com> - 0.6.23-6
- Typo fixes in spec: s/MULTI_SYMANTICS/MULTI_SEMANTICS/

* Tue Sep 13 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.23-5
- Trivial fixes in spec

* Sat Aug 27 2016 Neal Gompa <ngompa13@gmail.com> - 0.6.23-4
- Enable suserepo on Fedora to enable making openSUSE containers with Zypper

* Fri Aug 12 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.23-3
- Enable helixrepo on Fedora

* Wed Aug 03 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.23-2
- Backport patch to fix dnf --debugsolver crash (RHBZ #1361831)

* Wed Jul 27 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.23-1
- Update to 0.6.23

* Wed Jul 20 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.22-3
- Backport couple of patches from upstream

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.22-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Jun 14 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.22-1
- Update to 0.6.22
- Backport patch which will help to not autoremove needed packages
  (RHBZ #1227066, #1284349)

* Mon Jun 06 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.21-3
- Enable deb/arch support for non-rhel distros

* Mon May 30 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.21-2
- Modify enabled/disabled features

* Wed May 18 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.21-1
- Update to 0.6.21

* Tue May 17 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.20-2
- Backport patch to fix crashing on reading some repos (RHBZ #1318662)
- Backport patch to fix installing multilib packages with weak deps
  (RHBZ #1325471)

* Sat Apr 09 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.20-1
- Update to 0.6.20

* Tue Apr 05 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.19-3
- Reorganize spec file
- Enable helixrepo feature
- enable appdata feature

* Tue Mar 8 2016 Jaroslav Mracek <jmracek@redhat.com> - 0.6.19-2
- Apply 9 patches from upstream

* Sat Feb 27 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.19-1
- Update to 0.6.19

* Tue Feb  2 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.6.15-6
- Explicitly add rubypick and ruubygems build dependencies

* Tue Jan 12 2016 Vít Ondruch <vondruch@redhat.com> - 0.6.15-5
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.3

* Sun Jan 10 2016 Dan Horák <dan[at]danny.cz> - 0.6.15-4
- fix build on non-Fedora with python3

* Tue Jan 05 2016 Jaroslav Mracek <jmracek@redhat.com> - 0.6.15-3
- Fix bz2 compression support for python3 (RhBug:1293652)

* Fri Dec 18 2015 Michal Luscon <mluscon@redhat.com> - 0.6.15-2
- Revert reworked multiversion orphaned handling

* Thu Dec 17 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.15-1
- Update to 0.6.15

* Tue Dec 08 2015 Jaroslav Mracek <jmracek@redhat.com> - 0.6.14-7
- Rebase to upstream b1ea392
- Enable bz2 compression support (Mikolaj Izdebski <mizdebsk@redhat.com>) (RhBug:1226647)

* Thu Nov 26 2015 Adam Williamson <awilliam@redhat.com> - 0.6.14-6
- revert obsolete, as %%python_provide does it (undocumented)

* Wed Nov 18 2015 Adam Williamson <awilliam@redhat.com> - 0.6.14-5
- adjust obsolete for stupid packaging

* Wed Nov 18 2015 Adam Williamson <awilliam@redhat.com> - 0.6.14-4
- python2-solv obsoletes python-solv (#1263230)

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.14-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Wed Oct 14 2015 Michal Luscon <mluscon@redhat.com> - 0.6.14-2
- Backport patches from upstream

* Mon Oct 12 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.14-1
- Update to 0.6.14
- Backport patches from upstream

* Thu Sep 10 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.12-1
- Update to 0.6.12

* Wed Aug 05 2015 Jan Silhan <jsilhan@redhat.com> - 0.6.11-3
- added compile flag to support rich dependencies
- new version adding MIPS support
- Distribute testsolv in -tools subpackage (Igor Gnatenko)
- Enable python3 bindings for fedora (Igor Gnatenko)

* Tue Aug 04 2015 Adam Williamson <awilliam@redhat.com> - 0.6.11-2
- make bindings require the exact matching version of the lib (#1243737)

* Mon Jun 22 2015 Jan Silhan <jsilhan@redhat.com> - 0.6.11-1
- new version fixing segfault
- RbConfig fixed in the upstream (1928f1a), libsolv-ruby22-rbconfig.patch erased

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Mar 25 2015 Jan Silhan <jsilhan@redhat.com> - 0.6.10-1
- new version fixing segfault

* Fri Mar 6 2015 Jan Silhan <jsilhan@redhat.com> - 0.6.8-3
- Rebuilt with new provides selection feature

* Mon Jan 19 2015 Vít Ondruch <vondruch@redhat.com> - 0.6.8-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.2

* Fri Jan 16 2015 Richard Hughes <richard@hughsie.com> - 0.6.8-2
- Update to latest upstream release to fix a crash in PackageKit.

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild


* Mon Aug 11 2014 Jan Silhan <jsilhan@redhat.com> - 0.6.4-2
- Rebase to upstream 12af31a

* Mon Jul 28 2014 Aleš Kozumplík <akozumpl@redhat.com> - 0.6.4-1
- Rebase to upstream 5bd9589

* Mon Jul 14 2014 Jan Silhan <jsilhan@redhat.com> - 0.6.4-0.git2a5c1c4
- Rebase to upstream 2a5c1c4
- Filename selector can start with a star

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.1-2.git6d968f1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 27 2014 Aleš Kozumplík <ales@redhat.com> - 0.6.1-1.git6d968f1
- Rebase to upstream 6d968f1
- Fix RhBug:1049209

* Fri Apr 25 2014 Jan Silhan <jsilhan@redhat.com> - 0.6.1-0.gitf78f5de
- Rebase to 0.6.0, upstream commit f78f5de.

* Thu Apr 24 2014 Vít Ondruch <vondruch@redhat.com> - 0.6.0-0.git05baf54.1
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.1

* Wed Apr 9 2014 Jan Silhan <jsilhan@redhat.com> - 0.6.0-0.git05baf54
- Rebase to 0.6.0, upstream commit 05baf54.

* Mon Dec 16 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.4.1-1.gitbcedc98
- Rebase upstream bcedc98
- Fix RhBug:1051917.

* Mon Dec 16 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.4.1-0.gita8e47f1
- Rebase to 0.4.1, upstream commit a8e47f1.

* Fri Nov 22 2013 Zdenek Pavlas <zpavlas@redhat.com> - 0.4.0-2.git4442b7f
- Rebase to 0.4.0, upstream commit 4442b7f.
- support DELTA_LOCATION_BASE for completeness

* Tue Oct 29 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.4.0-1.gitd49d319
- Rebase to 0.4.0, upstream commit d49d319.

* Sat Aug 03 2013 Petr Pisar <ppisar@redhat.com> - 0.3.0-9.gita59d11d
- Perl 5.18 rebuild

* Wed Jul 31 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.3.0-8.gita59d11d
- Rebase to upstream a59d11d.

* Fri Jul 19 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.3.0-7.git228d412
- Add build flags, including Deb, Arch, LZMA and MULTI_SEMANTICS. (RhBug:985905)

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 0.3.0-6.git228d412
- Perl 5.18 rebuild

* Mon Jun 24 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.3.0-5.git228d412
- Rebase to upstream 228d412.
- Fixes hawkey github issue https://github.com/akozumpl/hawkey/issues/13

* Thu Jun 20 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.3.0-4.git209e9cb
- Rebase to upstream 209e9cb.
- Package the new man pages.

* Thu May 16 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.3.0-3.git7399ad1
- Run 'make test' with libsolv build.

* Mon Apr 8 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.3.0-2.git7399ad1
- Rebase to upstream 7399ad1.
- Fixes RhBug:905209

* Mon Apr 8 2013 Aleš Kozumplík <akozumpl@redhat.com> - 0.3.0-1.gite372b78
- Rebase to upstream e372b78.
- Fixes RhBug:e372b78

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.3-2.gitf663ca2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Aug 23 2012 Aleš Kozumplík <akozumpl@redhat.com> - 0.0.0-17.git6c9d3eb
- Rebase to upstream 6c9d3eb.
- Drop the solv.i stdbool.h fix integrated upstream.
- Dropped the job reasons fix.

* Mon Jul 23 2012 Aleš Kozumplík <akozumpl@redhat.com> - 0.0.0-16.git1617994
- Fix build problems with Perl bindings.

* Mon Jul 23 2012 Aleš Kozumplík <akozumpl@redhat.com> - 0.0.0-15.git1617994
- Rebuilt after a failed mass rebuild.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.0-14.git1617994
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul 16 2012 Aleš Kozumplik <akozumpl@redhat.com> - 0.0.0-13.git1617994%{?dist}
- preliminary fix for JOB resons in solver_describe_decision().

* Sun Jul 1 2012 Aleš Kozumplik <akozumpl@redhat.com> - 0.0.0-12.git1617994%{?dist}
- Rebase to upstream 1617994.
- Support for RPM_ADD_WITH_HDRID.

* Thu Jun  7 2012 Aleš Kozumplik <akozumpl@redhat.com> - 0.0.0-11.gitd39a42b%{?dist}
- Rebase to upstream d39a42b.
- Fix the epochs.
- Move the ruby modules into vendorarch dir, where they are expected.

* Thu May  17 2012 Aleš Kozumplik <akozumpl@redhat.com> - 0.0.0-9.git8cf7650%{?dist}
- Rebase to upstream 8cf7650.
- ruby bindings: fix USE_VENDORDIRS for Fedora.

* Thu Apr  12 2012 Aleš Kozumplik <akozumpl@redhat.com> - 0.0.0-7.gitaf1465a2%{?dist}
- Rebase to the upstream.
- Make repo_add_solv() work without stub repodata.

* Thu Apr  5 2012 Karel Klíč <kklic@redhat.com> - 0.0.0-6.git80afaf7%{?dist}
- Rebuild for the new libdb package.

* Mon Apr  2 2012 Karel Klíč <kklic@redhat.com> - 0.0.0-5.git80afaf7%{?dist}
- Rebuild for the new rpm package.

* Wed Mar 21 2012 Aleš Kozumplík <akozumpl@redhat.com> - 0.0.0-4.git80afaf7%{?dist}
- New upstream version, fix the .rpm release number.

* Wed Mar 21 2012 Aleš Kozumplík <akozumpl@redhat.com> - 0.0.0-3.git80afaf7%{?dist}
- New upstream version.

* Tue Feb  7 2012 Karel Klíč <kklic@redhat.com> - 0.0.0-2.git857fe28%{?dist}
- Adapted to Ruby 1.9.3 (workaround for broken CMake in Fedora and
  ruby template correction in bindings)

* Thu Feb  2 2012 Karel Klíč <kklic@redhat.com> - 0.0.0-1.git857fe28
- Initial packaging
- Based on Jindra Novy's spec file
- Based on upstream spec file
