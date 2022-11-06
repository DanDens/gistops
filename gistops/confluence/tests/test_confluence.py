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
import publishing


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


class FakeConfluenceApi:
    """ Replaces actual Confluence API for testing """

    def attach_file(self,
      filepath: str, 
      name: str, 
      page_id: str, 
      comment: str):
        """ Attaches a file to page """
        assert len(comment)>0

        assert Path(name).suffix in ['.pdf','.png']

        if page_id == '117606000':
            assert filepath in [
              '.gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf',
              'howtos/how-to-setup-a-scalable-vpc-architecture/2022-10-28 19_26_26-snaphot.png'
            ]
            return
        if page_id == '117607000':
            assert filepath in [
              '.gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf'
            ]
            return

        pytest.fail(f'Unexpected page id {page_id}')
            

    def update_or_create(self,
      parent_id: str,
      title: str,
      body: str, 
      representation: str) -> dict:
        """ Update or create page """

        assert representation == 'wiki'
        assert len(body)>0
        assert parent_id == '117605798'

        if title=='How to setup a scalable vpc architecture':
            return {
              'id': '117606000'
            }

        if title=='How to zip directories recursively with hidden files':
            return {
              'id': '117607000'
            }

        pytest.fail(f'Unexpected title {title}')

    def get_page_space(self, page_id: str) -> str:
        """ Returns the confluence space id of a page """

        assert page_id == '117605798'
        return 'docs'


    def get_page_id(self, space: str, title: str) -> str:
        """ Returns the confluence page id for page title and space """
        assert space == 'docs'
        
        if title=='How to setup a scalable vpc architecture':
            return '117606000'
        if title=='How to zip directories recursively with hidden files':
            return '117607000'

        pytest.fail(f'Unexpected title {title}')


def test_confluence_publish(mocker):
    """Tests all gists are converted"""
    
    in_base64 = \
      'eyJzZW12ZXIiOiAiMC4xLjAtYmV0YSIsICJyZWNvcmQtd'\
      'HlwZSI6ICJDb252ZXJ0ZWRHaXN0IiwgInJlY29yZHMiOi'\
      'BbeyJnaXN0IjogeyJwYXRoIjogImhvd3Rvcy9ob3ctdG8'\
      'tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJl'\
      'L1JFQURNRS5tZCIsICJjb21taXRfaWQiOiAiY2NhYjQ0Z'\
      'SIsICJ0YWdzIjogeyJjb25mbHVlbmNlIjogeyJwYWdlIj'\
      'ogIjExNzYwNTc5OCIsICJob3N0IjogInZlcncuYnNzbi5'\
      'ldSJ9fX0sICJwYXRoIjogIi5naXN0b3BzL2RhdGEvaG93'\
      'dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hc'\
      'mNoaXRlY3R1cmUvUkVBRE1FLnBkZiIsICJ0aXRsZSI6IC'\
      'JIb3cgdG8gc2V0dXAgYSBzY2FsYWJsZSB2cGMgYXJjaGl'\
      '0ZWN0dXJlIiwgImRlcHMiOiBbImhvd3Rvcy9ob3ctdG8t'\
      'c2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlI'\
      'iwgImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS'\
      '12cGMtYXJjaGl0ZWN0dXJlL2ltZyJdfSwgeyJnaXN0Ijo'\
      'geyJwYXRoIjogImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1z'\
      'Y2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZ'\
      'CIsICJjb21taXRfaWQiOiAiY2NhYjQ0ZSIsICJ0YWdzIj'\
      'ogeyJjb25mbHVlbmNlIjogeyJwYWdlIjogIjExNzYwNTc'\
      '5OCIsICJob3N0IjogInZlcncuYnNzbi5ldSJ9fX0sICJw'\
      'YXRoIjogIi5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10b'\
      'y1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cm'\
      'UvUkVBRE1FLmppcmEiLCAidGl0bGUiOiAiSG93IHRvIHN'\
      'ldHVwIGEgc2NhbGFibGUgdnBjIGFyY2hpdGVjdHVyZSIs'\
      'ICJkZXBzIjogWyJob3d0b3MvaG93LXRvLXNldHVwLWEtc'\
      '2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZSIsICJob3d0b3'\
      'MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2h'\
      'pdGVjdHVyZS9pbWciXX0sIHsiZ2lzdCI6IHsicGF0aCI6'\
      'ICJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZ'\
      'WN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETU'\
      'UubWQiLCAiY29tbWl0X2lkIjogImNjYWI0NGUiLCAidGF'\
      'ncyI6IHsiY29uZmx1ZW5jZSI6IHsicGFnZSI6ICIxMTc2'\
      'MDU3OTgiLCAiaG9zdCI6ICJ2ZXJ3LmJzc24uZXUifX19L'\
      'CAicGF0aCI6ICIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3'\
      'ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXd'\
      'pdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5wZGYiLCAidGl0'\
      'bGUiOiAiSG93IHRvIHppcCBkaXJlY3RvcmllcyByZWN1c'\
      'nNpdmVseSB3aXRoIGhpZGRlbiBmaWxlcyIsICJkZXBzIj'\
      'ogWyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1'\
      'yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcyIsICJo'\
      'b3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1c'\
      'nNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9pbWciXX0sIH'\
      'siZ2lzdCI6IHsicGF0aCI6ICJob3d0b3MvaG93LXRvLXp'\
      'pcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhp'\
      'ZGRlbi1maWxlcy9SRUFETUUubWQiLCAiY29tbWl0X2lkI'\
      'jogImNjYWI0NGUiLCAidGFncyI6IHsiY29uZmx1ZW5jZS'\
      'I6IHsicGFnZSI6ICIxMTc2MDU3OTgiLCAiaG9zdCI6ICJ'\
      '2ZXJ3LmJzc24uZXUifX19LCAicGF0aCI6ICIuZ2lzdG9w'\
      'cy9kYXRhL2hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9ya'\
      'WVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1'\
      'JFQURNRS5qaXJhIiwgInRpdGxlIjogIkhvdyB0byB6aXA'\
      'gZGlyZWN0b3JpZXMgcmVjdXJzaXZlbHkgd2l0aCBoaWRk'\
      'ZW4gZmlsZXMiLCAiZGVwcyI6IFsiaG93dG9zL2hvdy10b'\
      'y16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC'\
      '1oaWRkZW4tZmlsZXMiLCAiaG93dG9zL2hvdy10by16aXA'\
      'tZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRk'\
      'ZW4tZmlsZXMvaW1nIl19XX0='

    # Base64 encoding of
    # {"semver": "0.1.0-beta", "record-type": "ConvertedGist", "records": [
    # {
    #   "gist": {
    #     "path": "howtos/how-to-setup-a-scalable-vpc-architecture/README.md", 
    #     "commit_id": "ccab44e", 
    #     "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #   }, 
    #   "path": ".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf",   
    #   "title": "How to setup a scalable vpc architecture", 
    #   "deps": [
    #     "howtos/how-to-setup-a-scalable-vpc-architecture", 
    #     "howtos/how-to-setup-a-scalable-vpc-architecture/img"
    #   ]
    # }, {
    #   "gist": {
    #     "path": "howtos/how-to-setup-a-scalable-vpc-architecture/README.md", 
    #     "commit_id": "ccab44e", 
    #     "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #   }, 
    #   "path": ".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.jira", 
    #   "title": "How to setup a scalable vpc architecture", 
    #   "deps": [
    #     "howtos/how-to-setup-a-scalable-vpc-architecture", 
    #     "howtos/how-to-setup-a-scalable-vpc-architecture/img"
    #   ]
    # }, {
    #   "gist": {
    #     "path": "howtos/how-to-zip-directories-recursively-with-hidden-files/README.md", 
    #     "commit_id": "ccab44e", 
    #     "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #   }, 
    #   "path": ".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf", 
    #   "title": "How to zip directories recursively with hidden files", 
    #   "deps": [
    #     "howtos/how-to-zip-directories-recursively-with-hidden-files", 
    #     "howtos/how-to-zip-directories-recursively-with-hidden-files/img"
    #   ]
    # }, {
    #   "gist": {
    #     "path": "howtos/how-to-zip-directories-recursively-with-hidden-files/README.md", 
    #     "commit_id": "ccab44e", 
    #     "tags": {"confluence": {"page": "117605798", "host": "verw.bssn.eu"}}
    #   }, 
    #   "path": ".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.jira", 
    #   "title": "How to zip directories recursively with hidden files", 
    #   "deps": [
    #     "howtos/how-to-zip-directories-recursively-with-hidden-files", 
    #     "howtos/how-to-zip-directories-recursively-with-hidden-files/img"
    #   ]
    # }
    # ]}

    def __connect_to_api( url: str, username: str, password: str ):
        assert username == 'unknown'
        assert password == 'unknown'

        return publishing.ConfluenceAPI(
          url=url, api=FakeConfluenceApi() )


    mocker.patch('publishing.connect_to_api', side_effect=__connect_to_api)

    main.GistOps(cwd=str(Path.cwd())).run( 
      event_base64=in_base64,
      confluence_url='https://verw.bssn.eu/wiki',
      confluence_username='unknown',
      confluence_password='unknown' )
