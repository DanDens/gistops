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


def test_pandoc_convert():
    """Tests all gists are converted"""
    
    in_base64 = \
      'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLX' \
      'R5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6' \
      'Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS' \
      '12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsInRh' \
      'Z3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3Nj' \
      'A1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwi' \
      'Y29tbWl0X2lkIjoiNjA4YWJiOSJ9LHsicGF0aCI6Im' \
      'hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJl' \
      'Y3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQU' \
      'RNRS5tZCIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJw' \
      'YWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYn' \
      'Nzbi5ldSJ9fSwiY29tbWl0X2lkIjoiNjA4YWJiOSJ9' \
      'LHsicGF0aCI6InNvbWUgbm90ZWJvb2tzL3NvbWUta3' \
      'Bpcy9rcGlzLmlweW5iLmh0bWwiLCJ0YWdzIjp7fSwi' \
      'Y29tbWl0X2lkIjoiNjA4YWJiOSJ9XX0='
    
    # Base64 encoding of ...
    # {
    #     "semver":"0.1.0-beta",
    #     "record-type":"Gist",
    #     "records":[
    #         {
    #             "path":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md",
    #             "tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},
    #             "commit_id":"608abb9"
    #         },{
    #             "path":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md",
    #             "tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},
    #             "commit_id":"608abb9"
    #         },{
    #             "path":"some notebooks/some-kpis/kpis.ipynb.html",
    #             "tags":{},
    #             "commit_id":"608abb9"
    #         }
    #     ]
    # }

    out_base64:str = main.GistOps(cwd=str(Path.cwd())).run(
      event_base64=in_base64, 
      outpath=str(Path.cwd().joinpath('.gistops/data')))

    assert Path.cwd().joinpath('pandoc.gistops.trail').exists()
    assert Path.cwd().joinpath('pandoc.gistops.log').exists()

    assert out_base64 == \
      'eyJzZW12ZXIiOiAiMC4xLjAtYmV0YSIsICJyZWNvcmQtdHlwZSI6ICJDb' \
      '252ZXJ0ZWRHaXN0IiwgInJlY29yZHMiOiBbeyJnaXN0IjogeyJwYXRoIj' \
      'ogImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl' \
      '0ZWN0dXJlL1JFQURNRS5tZCIsICJjb21taXRfaWQiOiAiNjA4YWJiOSIs' \
      'ICJ0YWdzIjogeyJjb25mbHVlbmNlIjogeyJwYWdlIjogIjExNzYwNTc5O' \
      'CIsICJob3N0IjogInZlcncuYnNzbi5ldSJ9fX0sICJwYXRoIjogIi5naX' \
      'N0b3BzL2RhdGEvaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZ' \
      'wYy1hcmNoaXRlY3R1cmUvUkVBRE1FLnBkZiIsICJ0aXRsZSI6ICJIb3cg' \
      'dG8gc2V0dXAgYSBzY2FsYWJsZSB2cGMgYXJjaGl0ZWN0dXJlIiwgImRlc' \
      'HMiOiBbImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYX' \
      'JjaGl0ZWN0dXJlIiwgImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJ' \
      'sZS12cGMtYXJjaGl0ZWN0dXJlL2ltZyJdfSwgeyJnaXN0IjogeyJwYXRo' \
      'IjogImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJja' \
      'Gl0ZWN0dXJlL1JFQURNRS5tZCIsICJjb21taXRfaWQiOiAiNjA4YWJiOS' \
      'IsICJ0YWdzIjogeyJjb25mbHVlbmNlIjogeyJwYWdlIjogIjExNzYwNTc' \
      '5OCIsICJob3N0IjogInZlcncuYnNzbi5ldSJ9fX0sICJwYXRoIjogIi5n' \
      'aXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlL' \
      'XZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLmppcmEiLCAidGl0bGUiOiAiSG' \
      '93IHRvIHNldHVwIGEgc2NhbGFibGUgdnBjIGFyY2hpdGVjdHVyZSIsICJ' \
      'kZXBzIjogWyJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBj' \
      'LWFyY2hpdGVjdHVyZSIsICJob3d0b3MvaG93LXRvLXNldHVwLWEtc2Nhb' \
      'GFibGUtdnBjLWFyY2hpdGVjdHVyZS9pbWciXX0sIHsiZ2lzdCI6IHsicG' \
      'F0aCI6ICJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnN' \
      'pdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUubWQiLCAiY29tbWl0' \
      'X2lkIjogIjYwOGFiYjkiLCAidGFncyI6IHsiY29uZmx1ZW5jZSI6IHsic' \
      'GFnZSI6ICIxMTc2MDU3OTgiLCAiaG9zdCI6ICJ2ZXJ3LmJzc24uZXUifX' \
      '19LCAicGF0aCI6ICIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8teml' \
      'wLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVz' \
      'L1JFQURNRS5wZGYiLCAidGl0bGUiOiAiSG93IHRvIHppcCBkaXJlY3Rvc' \
      'mllcyByZWN1cnNpdmVseSB3aXRoIGhpZGRlbiBmaWxlcyIsICJkZXBzIj' \
      'ogWyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmV' \
      'seS13aXRoLWhpZGRlbi1maWxlcyIsICJob3d0b3MvaG93LXRvLXppcC1k' \
      'aXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9pb' \
      'WciXX0sIHsiZ2lzdCI6IHsicGF0aCI6ICJob3d0b3MvaG93LXRvLXppcC' \
      '1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9' \
      'SRUFETUUubWQiLCAiY29tbWl0X2lkIjogIjYwOGFiYjkiLCAidGFncyI6' \
      'IHsiY29uZmx1ZW5jZSI6IHsicGFnZSI6ICIxMTc2MDU3OTgiLCAiaG9zd' \
      'CI6ICJ2ZXJ3LmJzc24uZXUifX19LCAicGF0aCI6ICIuZ2lzdG9wcy9kYX' \
      'RhL2hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx' \
      '5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5qaXJhIiwgInRpdGxlIjog' \
      'IkhvdyB0byB6aXAgZGlyZWN0b3JpZXMgcmVjdXJzaXZlbHkgd2l0aCBoa' \
      'WRkZW4gZmlsZXMiLCAiZGVwcyI6IFsiaG93dG9zL2hvdy10by16aXAtZG' \
      'lyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMiLCA' \
      'iaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHkt' \
      'd2l0aC1oaWRkZW4tZmlsZXMvaW1nIl19LCB7Imdpc3QiOiB7InBhdGgiO' \
      'iAic29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXMuaXB5bmIuaHRtbC' \
      'IsICJjb21taXRfaWQiOiAiNjA4YWJiOSIsICJ0YWdzIjoge319LCAicGF' \
      '0aCI6ICIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb2tzL3NvbWUta3Bp' \
      'cy9rcGlzLmlweW5iLnBkZiIsICJ0aXRsZSI6ICJTb21lIGtwaXMiLCAiZ' \
      'GVwcyI6IFsic29tZSBub3RlYm9va3Mvc29tZS1rcGlzIl19LCB7Imdpc3' \
      'QiOiB7InBhdGgiOiAic29tZSBub3RlYm9va3Mvc29tZS1rcGlzL2twaXM' \
      'uaXB5bmIuaHRtbCIsICJjb21taXRfaWQiOiAiNjA4YWJiOSIsICJ0YWdz' \
      'Ijoge319LCAicGF0aCI6ICIuZ2lzdG9wcy9kYXRhL3NvbWUgbm90ZWJvb' \
      '2tzL3NvbWUta3Bpcy9rcGlzLmlweW5iLmppcmEiLCAidGl0bGUiOiAiU2' \
      '9tZSBrcGlzIiwgImRlcHMiOiBbInNvbWUgbm90ZWJvb2tzL3NvbWUta3B' \
      'pcyJdfV19'

    # Base64 encoding of
    # {
    #     "semver": "0.1.0-beta", 
    #     "record-type": "ConvertedGist", 
    #     "records": [
    #         {
    #         "gist": {
    #             "path": "howtos/how-to-setup-a-scalable-vpc-architecture/README.md", 
    #             "commit_id": "608abb9", 
    #             "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #             }, 
    #         "path": ".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf", 
    #         "title": "How to setup a scalable vpc architecture", 
    #         "deps": [
    #             "howtos/how-to-setup-a-scalable-vpc-architecture", 
    #             "howtos/how-to-setup-a-scalable-vpc-architecture/img"]
    #         }, {
    #         "gist": {
    #             "path": "howtos/how-to-setup-a-scalable-vpc-architecture/README.md", 
    #             "commit_id": "608abb9", 
    #             "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #           }, 
    #           "path": ".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.jira", 
    #           "title": "How to setup a scalable vpc architecture", 
    #           "deps": [
    #             "howtos/how-to-setup-a-scalable-vpc-architecture", 
    #             "howtos/how-to-setup-a-scalable-vpc-architecture/img"]
    #         }, {
    #         "gist": {
    #             "path": "howtos/how-to-zip-directories-recursively-with-hidden-files/README.md", 
    #             "commit_id": "608abb9", 
    #             "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #         }, 
    #         "path": ".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf", 
    #         "title": "How to zip directories recursively with hidden files", 
    #         "deps": [
    #             "howtos/how-to-zip-directories-recursively-with-hidden-files", 
    #             "howtos/how-to-zip-directories-recursively-with-hidden-files/img"]
    #         }, {
    #         "gist": {
    #             "path": "howtos/how-to-zip-directories-recursively-with-hidden-files/README.md", 
    #             "commit_id": "608abb9", 
    #             "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #         }, 
    #         "path": ".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.jira", 
    #         "title": "How to zip directories recursively with hidden files", 
    #         "deps": [
    #             "howtos/how-to-zip-directories-recursively-with-hidden-files", 
    #             "howtos/how-to-zip-directories-recursively-with-hidden-files/img"]
    #       }, {
    #         "gist": {
    #             "path": "some notebooks/some-kpis/kpis.ipynb.html", 
    #             "commit_id": "608abb9", 
    #             "tags": {}
    #         }, 
    #         "path": ".gistops/data/some notebooks/some-kpis/kpis.ipynb.pdf", 
    #         "title": "Some kpis", 
    #         "deps": [
    #             "some notebooks/some-kpis"]
    #       }, {
    #         "gist": {
    #             "path": "some notebooks/some-kpis/kpis.ipynb.html", 
    #             "commit_id": "608abb9", 
    #             "tags": {}
    #           }, 
    #           "path": ".gistops/data/some notebooks/some-kpis/kpis.ipynb.jira", 
    #           "title": "Some kpis", 
    #           "deps": [
    #             "some notebooks/some-kpis"]
    #       }
    #   ]
    # }
