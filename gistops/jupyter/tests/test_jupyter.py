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
    
    in_base64 = \
      'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHa' \
      'XN0IiwicmVjb3JkcyI6W3sicGF0aCI6InNvbWUgbm90ZWJvb2tzL3' \
      'NvbWUta3Bpcy9rcGlzLmlweW5iIiwidGFncyI6e30sImNvbW1pdF9' \
      'pZCI6IjM0NmU0ZWIifV19'
    
    # Base64 encoding of ...
    #{
    # "semver":"0.1.0-beta",
    # "record-type":"Gist",
    # "records":[
    #   {
    #     "path":"some notebooks/some-kpis/kpis.ipynb",
    #     "tags":{},
    #     "commit_id":"346e4eb"
    #   }
    # ]}

    out_base64:str = main.GistOps(cwd=str(Path.cwd())).run(
      event_base64=in_base64, 
      outpath=str(Path.cwd().joinpath('.gistops/data')))

    assert Path.cwd().joinpath('jupyter.gistops.trail').exists()
    assert Path.cwd().joinpath('jupyter.gistops.log').exists()

    assert out_base64 == \
      'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN' \
      '0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvc29tZS' \
      'Bub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIuaHRtbCIsInRhZ' \
      '3MiOnt9LCJjb21taXRfaWQiOiIzNDZlNGViIn1dfQ=='

    # Base64 encoding of ...
    #{
    # "semver":"0.1.0-beta",
    # "record-type":"Gist",
    # "records":[
    #   {
    #     "path":".gistops/data/some notebooks/some-kpis/kpis.ipynb.html",
    #     "tags":{},
    #     "commit_id":"346e4eb"
    #   }
    # ]}
