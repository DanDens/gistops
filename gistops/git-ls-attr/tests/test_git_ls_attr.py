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

    assert event_base64 == 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiY2NhYjQ0ZSIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZToqKi8qLioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUubWQiLCJ0aXRsZSI6Imhvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUtUkVBRE1FLm1kIn0seyJwYXRoIjoiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvUkVBRE1FLm1kIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiJjY2FiNDRlIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzOioqLyouKiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsInRpdGxlIjoiaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy1SRUFETUUubWQifV19'
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"ccab44e","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:**/*.*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"how-to-setup-a-scalable-vpc-architecture-README.md"},{"path":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"ccab44e","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:**/*.*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"how-to-zip-directories-recursively-with-hidden-files-README.md"}]}
    
    assert Path.cwd().joinpath('.gistops').joinpath('gists.json').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('git-ls-attr.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('git-ls-attr.gistops.log').exists()


def test_last_committed_gists_are_found():
    """Tests all gists are found"""
    
    event_base64:str = main.GistOps(
      cwd=str(Path.cwd())).list(git_hash='HEAD')
    
    assert event_base64 == 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Imhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiY2NhYjQ0ZSIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlczoqKi8qLioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUubWQiLCJ0aXRsZSI6Imhvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMtUkVBRE1FLm1kIn1dfQ=='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"ccab44e","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:**/*.*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"how-to-zip-directories-recursively-with-hidden-files-README.md"}]}

    assert Path.cwd().joinpath('.gistops').joinpath('git-ls-attr.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('git-ls-attr.gistops.log').exists()
    gists_json_path = Path.cwd().joinpath('.gistops').joinpath('gists.json')
    assert gists_json_path.exists()

    with open(str(gists_json_path),'r',encoding='utf-8') as gists_json_file:
        gists_json: list = json.loads(gists_json_file.read())

    assert len(gists_json) == 2
