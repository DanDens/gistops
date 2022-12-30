#!/usr/bin/env python3
"""
Tests for confluence gistops
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
def extract_repository():
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


def test_jupyter_convert():
    """Tests all jupyter gists are converted"""
    
    in_base64 = 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsInRhZ3MiOnsiamlyYSI6eyJpc3N1ZSI6IlVDQi0yMiIsImhvc3QiOiJ2ZXJ3LmJzc24uZXUifX0sImNvbW1pdF9pZCI6IjFjY2U4OTAiLCJyZXNvdXJjZXMiOlsiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmU6KiovKi4qIl0sInRyYWNlX2lkIjoiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLm1kIiwidGl0bGUiOiJob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlLVJFQURNRS5tZCJ9LHsicGF0aCI6Imhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsInRhZ3MiOnsiamlyYSI6eyJpc3N1ZSI6IlVDQi0yMyIsImhvc3QiOiJ2ZXJ3LmJzc24uZXUifX0sImNvbW1pdF9pZCI6IjFjY2U4OTAiLCJyZXNvdXJjZXMiOlsiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXM6KiovKi4qIl0sInRyYWNlX2lkIjoiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvUkVBRE1FLm1kIiwidGl0bGUiOiJob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzLVJFQURNRS5tZCJ9LHsicGF0aCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGFncyI6e30sImNvbW1pdF9pZCI6IjFjY2U4OTAiLCJyZXNvdXJjZXMiOlsic29tZSBub3RlYm9va3Mvc29tZS1rcGlzOioqLyouKiJdLCJ0cmFjZV9pZCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGl0bGUiOiJzb21lLWtwaXMta3Bpcy5pcHluYiJ9XX0='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","tags":{"jira":{"issue":"UCB-22","host":"verw.bssn.eu"}},"commit_id":"1cce890","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:**/*.*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"how-to-setup-a-scalable-vpc-architecture-README.md"},{"path":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","tags":{"jira":{"issue":"UCB-23","host":"verw.bssn.eu"}},"commit_id":"1cce890","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:**/*.*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"how-to-zip-directories-recursively-with-hidden-files-README.md"},{"path":"some notebooks/some-kpis/kpis.ipynb","tags":{},"commit_id":"1cce890","resources":["some notebooks/some-kpis:**/*.*"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"some-kpis-kpis.ipynb"}]}

    out_base64:str = main.GistOps(cwd=str(Path.cwd())).run(event_base64=in_base64,launch=True)

    assert Path.cwd().joinpath('.gistops').joinpath('jupyter.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('jupyter.gistops.log').exists()

    assert out_base64 == 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvc29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIubWQiLCJ0YWdzIjp7fSwiY29tbWl0X2lkIjoiMWNjZTg5MCIsInJlc291cmNlcyI6WyIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb2tzL3NvbWUta3BpczpvdXRwdXRfMl8wLnBuZyJdLCJ0cmFjZV9pZCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGl0bGUiOiJzb21lLWtwaXMta3Bpcy5pcHluYiJ9XX0='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.md","tags":{},"commit_id":"1cce890","resources":[".gistops/data/some notebooks/some-kpis:output_2_0.png"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"some-kpis-kpis.ipynb"}]}
