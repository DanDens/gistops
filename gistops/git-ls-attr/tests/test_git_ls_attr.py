#!/usr/bin/env python3
"""
Tests for git-ls-attr gistops image
"""
import os
import sys
import zipfile
import shutil
import json
from pathlib import Path

import pytest

sys.path.append(
  str(Path(os.path.realpath(__file__)).parent.parent.joinpath('gistops')))

import gists
import main


@pytest.fixture(scope="module", autouse=True)
def extract_git_ls_attr_repository():
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


def test_git_root():
    """Tests whether git root directory can be found"""
    
    git_root_path = gists.assert_git_root(Path.cwd().joinpath(
      'howtos').joinpath('how-to-zip-directories-recursively-with-hidden-files'))
    
    assert git_root_path == Path.cwd()


def test_all_gists_are_found():
    """Tests all gists are found"""

    event_base64:str = main.GistOps(
      cwd=str(Path.cwd())).list()
    assert event_base64 == \
      'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHa' \
      'XN0IiwicmVjb3JkcyI6W3sicGF0aCI6Imhvd3Rvcy9ob3ctdG8tc2' \
      'V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5' \
      'tZCIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1' \
      'Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkI' \
      'joiY2NhYjQ0ZSJ9LHsicGF0aCI6Imhvd3Rvcy9ob3ctdG8temlwLW' \
      'RpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGV' \
      'zL1JFQURNRS5tZCIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdl' \
      'IjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY' \
      '29tbWl0X2lkIjoiY2NhYjQ0ZSJ9XX0='
    # Base64 encoding of ...
    #{"semver":"0.1.0-beta","record-type":"Gist","records":[{
    #   "path":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md",
    #   "tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},
    #   "commit_id":"ccab44e"
    # },{
    #   "path":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md",
    #   "tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},
    #   "commit_id":"ccab44e"
    # }]}

    assert Path.cwd().joinpath('gists.json').exists()
    assert Path.cwd().joinpath('gistops.trail').exists()
    assert Path.cwd().joinpath('gistops.log').exists()


def test_last_committed_gists_are_found():
    """Tests all gists are found"""
    
    event_base64:str = main.GistOps(
      cwd=str(Path.cwd())).list(git_hash='HEAD')
    assert event_base64 == \
      'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJ' \
      'HaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Imhvd3Rvcy9ob3ctdG' \
      '8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZ' \
      'GVuLWZpbGVzL1JFQURNRS5tZCIsInRhZ3MiOnsiY29uZmx1ZW5j' \
      'ZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnN' \
      'zbi5ldSJ9fSwiY29tbWl0X2lkIjoiY2NhYjQ0ZSJ9XX0='

    # Base64 encoding of ...
    # {"semver":"0.1.0-beta","record-type":"Gist","records":[{
    #   "path":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md",
    #   "tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},
    #   "commit_id":"ccab44e"
    # }]}

    assert Path.cwd().joinpath('gistops.trail').exists()
    assert Path.cwd().joinpath('gistops.log').exists()
    gists_json_path = Path.cwd().joinpath('gists.json')
    assert gists_json_path.exists()

    with open(str(gists_json_path),'r',encoding='utf-8') as gists_json_file:
        gists_json: list = json.loads(gists_json_file.read())

    assert len(gists_json) == 2
