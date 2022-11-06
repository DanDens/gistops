#!/usr/bin/env python3
"""
Tests for git-ls-attr gistops image
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


def test_pandoc_convert():
    """Tests all gists are converted"""
    
    in_base64 = \
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

    out_base64:str = main.GistOps(cwd=str(Path.cwd())).run(
      event_base64=in_base64, 
      outpath=str(Path.cwd().joinpath('.gistops/data')))

    assert out_base64 == \
      'eyJzZW12ZXIiOiAiMC4xLjAtYmV0YSIsICJyZWNvcmQtdHlwZSI6IC'\
      'JDb252ZXJ0ZWRHaXN0IiwgInJlY29yZHMiOiBbeyJnaXN0IjogeyJw'\
      'YXRoIjogImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cG'\
      'MtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsICJjb21taXRfaWQiOiAi'\
      'Y2NhYjQ0ZSIsICJ0YWdzIjogeyJjb25mbHVlbmNlIjogeyJwYWdlIj'\
      'ogIjExNzYwNTc5OCIsICJob3N0IjogInZlcncuYnNzbi5ldSJ9fX0s'\
      'ICJwYXRoIjogIi5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by1zZX'\
      'R1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLnBk'\
      'ZiIsICJ0aXRsZSI6ICJIb3cgdG8gc2V0dXAgYSBzY2FsYWJsZSB2cG'\
      'MgYXJjaGl0ZWN0dXJlIiwgImRlcHMiOiBbImhvd3Rvcy9ob3ctdG8t'\
      'c2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlIiwgImhvd3'\
      'Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0'\
      'dXJlL2ltZyJdfSwgeyJnaXN0IjogeyJwYXRoIjogImhvd3Rvcy9ob3'\
      'ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JF'\
      'QURNRS5tZCIsICJjb21taXRfaWQiOiAiY2NhYjQ0ZSIsICJ0YWdzIj'\
      'ogeyJjb25mbHVlbmNlIjogeyJwYWdlIjogIjExNzYwNTc5OCIsICJo'\
      'b3N0IjogInZlcncuYnNzbi5ldSJ9fX0sICJwYXRoIjogIi5naXN0b3'\
      'BzL2RhdGEvaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZw'\
      'Yy1hcmNoaXRlY3R1cmUvUkVBRE1FLmppcmEiLCAidGl0bGUiOiAiSG'\
      '93IHRvIHNldHVwIGEgc2NhbGFibGUgdnBjIGFyY2hpdGVjdHVyZSIs'\
      'ICJkZXBzIjogWyJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibG'\
      'UtdnBjLWFyY2hpdGVjdHVyZSIsICJob3d0b3MvaG93LXRvLXNldHVw'\
      'LWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9pbWciXX0sIHsiZ2'\
      'lzdCI6IHsicGF0aCI6ICJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rv'\
      'cmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETU'\
      'UubWQiLCAiY29tbWl0X2lkIjogImNjYWI0NGUiLCAidGFncyI6IHsi'\
      'Y29uZmx1ZW5jZSI6IHsicGFnZSI6ICIxMTc2MDU3OTgiLCAiaG9zdC'\
      'I6ICJ2ZXJ3LmJzc24uZXUifX19LCAicGF0aCI6ICIuZ2lzdG9wcy9k'\
      'YXRhL2hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2'\
      'l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5qaXJhIiwgInRp'\
      'dGxlIjogIkhvdyB0byB6aXAgZGlyZWN0b3JpZXMgcmVjdXJzaXZlbH'\
      'kgd2l0aCBoaWRkZW4gZmlsZXMiLCAiZGVwcyI6IFsiaG93dG9zL2hv'\
      'dy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaW'\
      'RkZW4tZmlsZXMiLCAiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3Jp'\
      'ZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvaW1nIl19LC'\
      'B7Imdpc3QiOiB7InBhdGgiOiAiaG93dG9zL2hvdy10by16aXAtZGly'\
      'ZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvUk'\
      'VBRE1FLm1kIiwgImNvbW1pdF9pZCI6ICJjY2FiNDRlIiwgInRhZ3Mi'\
      'OiB7ImNvbmZsdWVuY2UiOiB7InBhZ2UiOiAiMTE3NjA1Nzk4IiwgIm'\
      'hvc3QiOiAidmVydy5ic3NuLmV1In19fSwgInBhdGgiOiAiLmdpc3Rv'\
      'cHMvZGF0YS9ob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZW'\
      'N1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUucGRmIiwg'\
      'InRpdGxlIjogIkhvdyB0byB6aXAgZGlyZWN0b3JpZXMgcmVjdXJzaX'\
      'ZlbHkgd2l0aCBoaWRkZW4gZmlsZXMiLCAiZGVwcyI6IFsiaG93dG9z'\
      'L2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC'\
      '1oaWRkZW4tZmlsZXMiLCAiaG93dG9zL2hvdy10by16aXAtZGlyZWN0'\
      'b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvaW1nIl'\
      '19XX0='

    # Base64 encoding of
    # {"semver": "0.1.0-beta", "record-type": "ConvertedGist", "records": [
    #   {
    #     "gist": {
    #       "path": "howtos/how-to-setup-a-scalable-vpc-architecture/README.md", 
    #       "commit_id": "ccab44e", 
    #       "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #     }, 
    #     "path": ".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf", 
    #     "title": "How to setup a scalable vpc architecture", 
    #     "deps": [
    #       "howtos/how-to-setup-a-scalable-vpc-architecture", 
    #       "howtos/how-to-setup-a-scalable-vpc-architecture/img"
    #     ]
    #   }, {
    #     "gist": {
    #       "path": "howtos/how-to-setup-a-scalable-vpc-architecture/README.md", 
    #       "commit_id": "ccab44e", 
    #       "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #     }, 
    #     "path": ".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.jira", 
    #     "title": "How to setup a scalable vpc architecture", 
    #     "deps": [
    #       "howtos/how-to-setup-a-scalable-vpc-architecture", 
    #       "howtos/how-to-setup-a-scalable-vpc-architecture/img"
    #     ]
    #   }, {
    #     "gist": {
    #       "path": "howtos/how-to-zip-directories-recursively-with-hidden-files/README.md", 
    #       "commit_id": "ccab44e", 
    #       "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #     }, 
    #     "path": ".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.jira", 
    #     "title": "How to zip directories recursively with hidden files", 
    #     "deps": [
    #       "howtos/how-to-zip-directories-recursively-with-hidden-files", 
    #       "howtos/how-to-zip-directories-recursively-with-hidden-files/img"
    #     ]
    #   }, {
    #     "gist": {
    #       "path": "howtos/how-to-zip-directories-recursively-with-hidden-files/README.md", 
    #       "commit_id": "ccab44e", 
    #       "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #     }, 
    #     "path": ".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf", 
    #     "title": "How to zip directories recursively with hidden files", 
    #     "deps": [
    #       "howtos/how-to-zip-directories-recursively-with-hidden-files", 
    #       "howtos/how-to-zip-directories-recursively-with-hidden-files/img"
    #     ]
    #   }
    # ]}
