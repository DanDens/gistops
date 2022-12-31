#!/usr/bin/env python3
"""
Tests for pandoc gistops
"""
import os
import sys
import zipfile
import shutil
from pathlib import Path

import pytest

sys.path.append(
  str(Path(os.path.realpath(__file__)).parent.parent.joinpath('gistops')))

import main


@pytest.fixture(scope="module", autouse=True)
def extract_pandoc_repository():
    """Unpacks git repository used for tests as repos/*.repo"""
    # Unpack git repository
    this_filepath = Path(os.path.realpath(__file__))
    
    this_reposdir = this_filepath.parent.joinpath('repos')
    this_repozip = this_reposdir.joinpath(f'{this_filepath.stem}.zip')
    this_repopath = this_reposdir.joinpath(f'{this_filepath.stem}.unpack')

    with zipfile.ZipFile(this_repozip,'r') as repo_zip:
        repo_zip.extractall( path=this_repopath )

    # Switch working directory to repository
    old_cwd = os.getcwd()
    os.chdir(str(this_repopath))

    yield # Run the tests and come back to clean up ...

    # Switch back 
    os.chdir(old_cwd)

    # Remove unpacked git repo
    shutil.rmtree(this_repopath)


def test_pandoc_markdown_convert():
    """Tests markdown gists are converted"""
    
    in_base64 = 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZToqKi8qLioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUubWQiLCJ0aXRsZSI6Imhvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUtUkVBRE1FLm1kIn0seyJwYXRoIjoiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvUkVBRE1FLm1kIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiI2Y2QwMTRkIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzOioqLyouKiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsInRpdGxlIjoiaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy1SRUFETUUubWQifSx7InBhdGgiOiJzb21lIG5vdGVib29rcy9zb21lLWtwaXMva3Bpcy5pcHluYiIsInRhZ3MiOnt9LCJjb21taXRfaWQiOiI2Y2QwMTRkIiwicmVzb3VyY2VzIjpbInNvbWUgbm90ZWJvb2tzL3NvbWUta3BpczoqKi8qLioiXSwidHJhY2VfaWQiOiJzb21lIG5vdGVib29rcy9zb21lLWtwaXMva3Bpcy5pcHluYiIsInRpdGxlIjoic29tZS1rcGlzLWtwaXMuaXB5bmIifV19'
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:**/*.*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"how-to-setup-a-scalable-vpc-architecture-README.md"},{"path":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:**/*.*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"how-to-zip-directories-recursively-with-hidden-files-README.md"},{"path":"some notebooks/some-kpis/kpis.ipynb","tags":{},"commit_id":"6cd014d","resources":["some notebooks/some-kpis:**/*.*"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"some-kpis-kpis.ipynb"}]}

    out_base64:str = main.GistOps(cwd=str(Path.cwd())).run(
      event_base64=in_base64)

    assert Path.cwd().joinpath('.gistops').joinpath('pandoc.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('pandoc.gistops.log').exists()

    assert out_base64 == 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLnBkZiIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZToqIiwiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvaW1nOioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUubWQiLCJ0aXRsZSI6IkhvdyB0byBzZXR1cCBhIHNjYWxhYmxlIHZwYyBhcmNoaXRlY3R1cmUifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5qaXJhIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiI2Y2QwMTRkIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlOioiLCJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9pbWc6KiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsInRpdGxlIjoiSG93IHRvIHNldHVwIGEgc2NhbGFibGUgdnBjIGFyY2hpdGVjdHVyZSJ9LHsicGF0aCI6Ii5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvUkVBRE1FLnBkZiIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlczoqIiwiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvaW1nOioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUubWQiLCJ0aXRsZSI6IkhvdyB0byB6aXAgZGlyZWN0b3JpZXMgcmVjdXJzaXZlbHkgd2l0aCBoaWRkZW4gZmlsZXMifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5qaXJhIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiI2Y2QwMTRkIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzOioiLCJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9pbWc6KiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsInRpdGxlIjoiSG93IHRvIHppcCBkaXJlY3RvcmllcyByZWN1cnNpdmVseSB3aXRoIGhpZGRlbiBmaWxlcyJ9XX0='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:*","howtos/how-to-setup-a-scalable-vpc-architecture/img:*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"How to setup a scalable vpc architecture"},{"path":".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.jira","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:*","howtos/how-to-setup-a-scalable-vpc-architecture/img:*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"How to setup a scalable vpc architecture"},{"path":".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:*","howtos/how-to-zip-directories-recursively-with-hidden-files/img:*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"How to zip directories recursively with hidden files"},{"path":".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.jira","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:*","howtos/how-to-zip-directories-recursively-with-hidden-files/img:*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"How to zip directories recursively with hidden files"}]}


def test_pandoc_ipynb_convert():
    """Tests ipynb gists are converted"""
    
    in_base64 = 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvc29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIubWQiLCJ0YWdzIjp7fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb2tzL3NvbWUta3BpczpvdXRwdXRfMl8wLnBuZyJdLCJ0cmFjZV9pZCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGl0bGUiOiJzb21lLWtwaXMta3Bpcy5pcHluYiJ9XX0='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.md","tags":{},"commit_id":"6cd014d","resources":[".gistops/data/some notebooks/some-kpis:output_2_0.png"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"some-kpis-kpis.ipynb"}]}

    out_base64:str = main.GistOps(cwd=str(Path.cwd())).run(
      event_base64=in_base64)

    assert Path.cwd().joinpath('.gistops').joinpath('pandoc.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('pandoc.gistops.log').exists()

    assert out_base64 == 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvc29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIucGRmIiwidGFncyI6e30sImNvbW1pdF9pZCI6IjZjZDAxNGQiLCJyZXNvdXJjZXMiOlsiLmdpc3RvcHMvZGF0YS9zb21lIG5vdGVib29rcy9zb21lLWtwaXM6KiJdLCJ0cmFjZV9pZCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGl0bGUiOiJTb21lIGtwaXMifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iLmppcmEiLCJ0YWdzIjp7fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb2tzL3NvbWUta3BpczoqIl0sInRyYWNlX2lkIjoic29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIiLCJ0aXRsZSI6IlNvbWUga3BpcyJ9XX0='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.pdf","tags":{},"commit_id":"6cd014d","resources":[".gistops/data/some notebooks/some-kpis:*"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"Some kpis"},{"path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.jira","tags":{},"commit_id":"6cd014d","resources":[".gistops/data/some notebooks/some-kpis:*"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"Some kpis"}]}


def test_pandoc_convert_join_events():
    """Tests all gists are converted"""
    
    in_base64 = [
      'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvc29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIubWQiLCJ0YWdzIjp7fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb2tzL3NvbWUta3BpczpvdXRwdXRfMl8wLnBuZyJdLCJ0cmFjZV9pZCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGl0bGUiOiJzb21lLWtwaXMta3Bpcy5pcHluYiJ9XX0=',
      'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZToqKi8qLioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUubWQiLCJ0aXRsZSI6Imhvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUtUkVBRE1FLm1kIn0seyJwYXRoIjoiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvUkVBRE1FLm1kIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiI2Y2QwMTRkIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzOioqLyouKiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsInRpdGxlIjoiaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy1SRUFETUUubWQifSx7InBhdGgiOiJzb21lIG5vdGVib29rcy9zb21lLWtwaXMva3Bpcy5pcHluYiIsInRhZ3MiOnt9LCJjb21taXRfaWQiOiI2Y2QwMTRkIiwicmVzb3VyY2VzIjpbInNvbWUgbm90ZWJvb2tzL3NvbWUta3BpczoqKi8qLioiXSwidHJhY2VfaWQiOiJzb21lIG5vdGVib29rcy9zb21lLWtwaXMva3Bpcy5pcHluYiIsInRpdGxlIjoic29tZS1rcGlzLWtwaXMuaXB5bmIifV19'
    ]
    # Base64 encoding of ... [
    #   {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.md","tags":{},"commit_id":"6cd014d","resources":[".gistops/data/some notebooks/some-kpis:output_2_0.png"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"some-kpis-kpis.ipynb"}]},
    #   {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:**/*.*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"how-to-setup-a-scalable-vpc-architecture-README.md"},{"path":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:**/*.*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"how-to-zip-directories-recursively-with-hidden-files-README.md"},{"path":"some notebooks/some-kpis/kpis.ipynb","tags":{},"commit_id":"6cd014d","resources":["some notebooks/some-kpis:**/*.*"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"some-kpis-kpis.ipynb"}]}
    # ]

    out_base64:str = main.GistOps(cwd=str(Path.cwd())).run(
      event_base64=in_base64)

    assert Path.cwd().joinpath('.gistops').joinpath('pandoc.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('pandoc.gistops.log').exists()

    assert out_base64 == 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvc29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIucGRmIiwidGFncyI6e30sImNvbW1pdF9pZCI6IjZjZDAxNGQiLCJyZXNvdXJjZXMiOlsiLmdpc3RvcHMvZGF0YS9zb21lIG5vdGVib29rcy9zb21lLWtwaXM6KiJdLCJ0cmFjZV9pZCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGl0bGUiOiJTb21lIGtwaXMifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iLmppcmEiLCJ0YWdzIjp7fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb2tzL3NvbWUta3BpczoqIl0sInRyYWNlX2lkIjoic29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIiLCJ0aXRsZSI6IlNvbWUga3BpcyJ9LHsicGF0aCI6Ii5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLnBkZiIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZToqIiwiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvaW1nOioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUubWQiLCJ0aXRsZSI6IkhvdyB0byBzZXR1cCBhIHNjYWxhYmxlIHZwYyBhcmNoaXRlY3R1cmUifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5qaXJhIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiI2Y2QwMTRkIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlOioiLCJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9pbWc6KiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsInRpdGxlIjoiSG93IHRvIHNldHVwIGEgc2NhbGFibGUgdnBjIGFyY2hpdGVjdHVyZSJ9LHsicGF0aCI6Ii5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvUkVBRE1FLnBkZiIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiNmNkMDE0ZCIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlczoqIiwiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvaW1nOioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUubWQiLCJ0aXRsZSI6IkhvdyB0byB6aXAgZGlyZWN0b3JpZXMgcmVjdXJzaXZlbHkgd2l0aCBoaWRkZW4gZmlsZXMifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5qaXJhIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiI2Y2QwMTRkIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzOioiLCJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9pbWc6KiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsInRpdGxlIjoiSG93IHRvIHppcCBkaXJlY3RvcmllcyByZWN1cnNpdmVseSB3aXRoIGhpZGRlbiBmaWxlcyJ9XX0='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.pdf","tags":{},"commit_id":"6cd014d","resources":[".gistops/data/some notebooks/some-kpis:*"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"Some kpis"},{"path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.jira","tags":{},"commit_id":"6cd014d","resources":[".gistops/data/some notebooks/some-kpis:*"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"Some kpis"},{"path":".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:*","howtos/how-to-setup-a-scalable-vpc-architecture/img:*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"How to setup a scalable vpc architecture"},{"path":".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.jira","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:*","howtos/how-to-setup-a-scalable-vpc-architecture/img:*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"How to setup a scalable vpc architecture"},{"path":".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:*","howtos/how-to-zip-directories-recursively-with-hidden-files/img:*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"How to zip directories recursively with hidden files"},{"path":".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.jira","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"6cd014d","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:*","howtos/how-to-zip-directories-recursively-with-hidden-files/img:*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"How to zip directories recursively with hidden files"}]}
