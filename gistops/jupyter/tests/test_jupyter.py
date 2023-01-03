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
    
    in_base64 = 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGFncyI6eyJqdXB5dGVyIjpbeyJmb3JtYXQiOiJtYXJrZG93biIsImxhdW5jaCI6dHJ1ZX1dfSwiY29tbWl0X2lkIjoiMzQ2ZTRlYiIsInJlc291cmNlcyI6WyJzb21lIG5vdGVib29rcy9zb21lLWtwaXM6KiovKi4qIl0sInRyYWNlX2lkIjoic29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIiLCJ0aXRsZSI6InNvbWUta3Bpcy1rcGlzLmlweW5iIn1dfQ=='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":"some notebooks/some-kpis/kpis.ipynb","tags":{"jupyter":[{"format":"markdown","launch":true}]},"commit_id":"346e4eb","resources":["some notebooks/some-kpis:**/*.*"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"some-kpis-kpis.ipynb"}]}

    out_base64:str = main.GistOps(cwd=str(Path.cwd())).run(event_base64=in_base64)

    assert Path.cwd().joinpath('.gistops').joinpath('jupyter.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('jupyter.gistops.log').exists()

    assert out_base64 == 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvc29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIubWQiLCJ0YWdzIjp7Imp1cHl0ZXIiOlt7ImZvcm1hdCI6Im1hcmtkb3duIiwibGF1bmNoIjp0cnVlfV19LCJjb21taXRfaWQiOiIzNDZlNGViIiwicmVzb3VyY2VzIjpbIi5naXN0b3BzL2RhdGEvc29tZSBub3RlYm9va3Mvc29tZS1rcGlzOm91dHB1dF8yXzAucG5nIl0sInRyYWNlX2lkIjoic29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIiLCJ0aXRsZSI6InNvbWUta3Bpcy1rcGlzLmlweW5iIn1dfQ=='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.md","tags":{"jupyter":[{"format":"markdown","launch":true}]},"commit_id":"346e4eb","resources":[".gistops/data/some notebooks/some-kpis:output_2_0.png"],"trace_id":"some notebooks/some-kpis/kpis.ipynb","title":"some-kpis-kpis.ipynb"}]}
