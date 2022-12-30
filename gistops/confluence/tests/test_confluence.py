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
    
    in_base64 = 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLnBkZiIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiY2NhYjQ0ZSIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZToqIiwiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvaW1nOioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUubWQiLCJ0aXRsZSI6IkhvdyB0byBzZXR1cCBhIHNjYWxhYmxlIHZwYyBhcmNoaXRlY3R1cmUifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5qaXJhIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiJjY2FiNDRlIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlOioiLCJob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9pbWc6KiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsInRpdGxlIjoiSG93IHRvIHNldHVwIGEgc2NhbGFibGUgdnBjIGFyY2hpdGVjdHVyZSJ9LHsicGF0aCI6Ii5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvUkVBRE1FLnBkZiIsInRhZ3MiOnsiY29uZmx1ZW5jZSI6eyJwYWdlIjoiMTE3NjA1Nzk4IiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiY2NhYjQ0ZSIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlczoqIiwiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvaW1nOioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUubWQiLCJ0aXRsZSI6IkhvdyB0byB6aXAgZGlyZWN0b3JpZXMgcmVjdXJzaXZlbHkgd2l0aCBoaWRkZW4gZmlsZXMifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5qaXJhIiwidGFncyI6eyJjb25mbHVlbmNlIjp7InBhZ2UiOiIxMTc2MDU3OTgiLCJob3N0IjoidmVydy5ic3NuLmV1In19LCJjb21taXRfaWQiOiJjY2FiNDRlIiwicmVzb3VyY2VzIjpbImhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzOioiLCJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9pbWc6KiJdLCJ0cmFjZV9pZCI6Imhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsInRpdGxlIjoiSG93IHRvIHppcCBkaXJlY3RvcmllcyByZWN1cnNpdmVseSB3aXRoIGhpZGRlbiBmaWxlcyJ9XX0='
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"ccab44e","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:*","howtos/how-to-setup-a-scalable-vpc-architecture/img:*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"How to setup a scalable vpc architecture"},{"path":".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.jira","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"ccab44e","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:*","howtos/how-to-setup-a-scalable-vpc-architecture/img:*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"How to setup a scalable vpc architecture"},{"path":".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"ccab44e","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:*","howtos/how-to-zip-directories-recursively-with-hidden-files/img:*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"How to zip directories recursively with hidden files"},{"path":".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.jira","tags":{"confluence":{"page":"117605798","host":"verw.bssn.eu"}},"commit_id":"ccab44e","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:*","howtos/how-to-zip-directories-recursively-with-hidden-files/img:*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"How to zip directories recursively with hidden files"}]}
    
    def __connect_to_api( url: str, access_token: str ):
        assert access_token == 'unknown'

        return publishing.ConfluenceAPI(
          url=url, api=FakeConfluenceApi() )


    mocker.patch('publishing.connect_to_api', side_effect=__connect_to_api)

    main.GistOps(cwd=str(Path.cwd())).run( 
      event_base64=in_base64,
      confluence_url='https://verw.bssn.eu/wiki',
      confluence_access_token='unknown' )

    assert Path.cwd().joinpath('.gistops').joinpath('confluence.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('confluence.gistops.log').exists()
