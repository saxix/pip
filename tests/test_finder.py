import os
from pkg_resources import parse_version
from pip.backwardcompat import urllib
from pip.req import InstallRequirement
from pip.index import PackageFinder
from pip.exceptions import BestVersionAlreadyInstalled
from tests.path import Path
from tests.test_pip import here, path_to_url
from nose.tools import assert_raises
from mock import Mock

find_links = path_to_url(os.path.join(here, 'packages'))
find_links2 = path_to_url(os.path.join(here, 'packages2'))


def test_no_mpkg():
    """Finder skips zipfiles with "macosx10" in the name."""
    finder = PackageFinder([find_links], [])
    req = InstallRequirement.from_line("pkgwithmpkg")
    found = finder.find_requirement(req, False)

    assert found.url.endswith("pkgwithmpkg-1.0.tar.gz"), found


def test_no_partial_name_match():
    """Finder requires the full project name to match, not just beginning."""
    finder = PackageFinder([find_links], [])
    req = InstallRequirement.from_line("gmpy")
    found = finder.find_requirement(req, False)

    assert found.url.endswith("gmpy-1.15.tar.gz"), found

def test_duplicates_sort_ok():
    """Finder successfully finds one of a set of duplicates in different
    locations"""
    finder = PackageFinder([find_links, find_links2], [])
    req = InstallRequirement.from_line("duplicate")
    found = finder.find_requirement(req, False)

    assert found.url.endswith("duplicate-1.0.tar.gz"), found


def test_finder_detects_latest_find_links():
    """Test PackageFinder detects latest using find-links"""
    req = InstallRequirement.from_line('simple', None)
    finder = PackageFinder([find_links], [])
    link = finder.find_requirement(req, False)
    assert link.url.endswith("simple-3.0.tar.gz")


def test_finder_detects_latest_already_satisfied_find_links():
    """Test PackageFinder detects latest already satisified using find-links"""
    req = InstallRequirement.from_line('simple', None)
    #the latest simple in local pkgs is 3.0
    latest_version = "3.0"
    satisfied_by = Mock(
        location = "/path",
        parsed_version = parse_version(latest_version),
        version = latest_version
        )
    req.satisfied_by = satisfied_by
    finder = PackageFinder([find_links], [])
    assert_raises(BestVersionAlreadyInstalled, finder.find_requirement, req, True)


def test_finder_detects_latest_already_satisfied_pypi_links():
    """Test PackageFinder detects latest already satisified using pypi links"""
    req = InstallRequirement.from_line('initools', None)
    #the latest initools on pypi is 0.3.1
    latest_version = "0.3.1"
    satisfied_by = Mock(
        location = "/path",
        parsed_version = parse_version(latest_version),
        version = latest_version
        )
    req.satisfied_by = satisfied_by
    finder = PackageFinder([], ["http://pypi.python.org/simple"])
    assert_raises(BestVersionAlreadyInstalled, finder.find_requirement, req, True)


def test_finder_priority_file_over_page():
    """Test PackageFinder prefers file links over equivalent page links"""
    req = InstallRequirement.from_line('gmpy==1.15', None)
    finder = PackageFinder([find_links], ["http://pypi.python.org/simple"])
    link = finder.find_requirement(req, False)
    assert link.url.startswith("file://")


def test_finder_priority_page_over_deplink():
    """Test PackageFinder prefers page links over equivalent dependency links"""
    req = InstallRequirement.from_line('gmpy==1.15', None)
    finder = PackageFinder([], ["http://pypi.python.org/simple"])
    finder.add_dependency_links(['http://c.pypi.python.org/simple/gmpy/'])
    link = finder.find_requirement(req, False)
    assert link.url.startswith("http://pypi")


def test_finder_priority_nonegg_over_eggfragments():
    """Test PackageFinder prefers non-egg links over "#egg=" links"""
    req = InstallRequirement.from_line('bar==1.0', None)
    links = ['http://foo/bar.py#egg=bar-1.0', 'http://foo/bar-1.0.tar.gz']

    finder = PackageFinder(links, [])
    link = finder.find_requirement(req, False)
    assert link.url.endswith('tar.gz')

    links.reverse()
    finder = PackageFinder(links, [])
    link = finder.find_requirement(req, False)
    assert link.url.endswith('tar.gz')



