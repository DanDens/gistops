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


class FakeJiraApi:
    """ Replaces actual Jira API for testing """

    def add_attachment(self, issue_key:str, filename=str):
        """ Attaches a file to jira issue """
        assert Path(filename).suffix in ['.pdf','.png']

        if issue_key == 'UCB-22':
            assert filename in [
              '.gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf',
              'howtos/how-to-setup-a-scalable-vpc-architecture/2022-10-28 19_26_26-snaphot.png'
            ]
            return
        if issue_key == 'UCB-23':
            assert filename in [
              '.gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf'
            ]
            return

        pytest.fail(f'Unexpected issue key {issue_key}')
            

    def update_issue_field(self, issue_key: str, fields: dict):
        """ Update issue field """

        assert 'description' in fields
        assert len(fields['description'])>0
        
        if issue_key=='UCB-22':
            return
        if issue_key=='UCB-23':
            return

        pytest.fail(f'Unexpected issue key {issue_key}')


def test_jira_publish(mocker):
    """Tests all gists are converted"""
    
    in_base64 = \
      'eyJzZW12ZXIiOiAiMC4xLjAtYmV0YSIsICJyZWNvcmQtdHlwZSI6ICJDb252ZXJ0ZWRHaXN0Iiwg'\
      'InJlY29yZHMiOiBbeyJnaXN0IjogeyJwYXRoIjogImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2Fs'\
      'YWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5tZCIsICJjb21taXRfaWQiOiAiY2NhYjQ0ZSIs'\
      'ICJ0YWdzIjogeyJqaXJhIjogeyJpc3N1ZSI6ICJVQ0ItMjIiLCAiaG9zdCI6ICJ2ZXJ3LmJzc24u'\
      'ZXUifX19LCAicGF0aCI6ICIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2Fs'\
      'YWJsZS12cGMtYXJjaGl0ZWN0dXJlL1JFQURNRS5wZGYiLCAidGl0bGUiOiAiSG93IHRvIHNldHVw'\
      'IGEgc2NhbGFibGUgdnBjIGFyY2hpdGVjdHVyZSIsICJkZXBzIjogWyJob3d0b3MvaG93LXRvLXNl'\
      'dHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZSIsICJob3d0b3MvaG93LXRvLXNldHVwLWEt'\
      'c2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9pbWciXX0sIHsiZ2lzdCI6IHsicGF0aCI6ICJob3d0'\
      'b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUubWQiLCAi'\
      'Y29tbWl0X2lkIjogImNjYWI0NGUiLCAidGFncyI6IHsiamlyYSI6IHsiaXNzdWUiOiAiVUNCLTIy'\
      'IiwgImhvc3QiOiAidmVydy5ic3NuLmV1In19fSwgInBhdGgiOiAiLmdpc3RvcHMvZGF0YS9ob3d0'\
      'b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUuamlyYSIs'\
      'ICJ0aXRsZSI6ICJIb3cgdG8gc2V0dXAgYSBzY2FsYWJsZSB2cGMgYXJjaGl0ZWN0dXJlIiwgImRl'\
      'cHMiOiBbImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlIiwg'\
      'Imhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL2ltZyJdfSwg'\
      'eyJnaXN0IjogeyJwYXRoIjogImhvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2'\
      'ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5tZCIsICJjb21taXRfaWQiOiAiY2NhYjQ0ZSIs'\
      'ICJ0YWdzIjogeyJqaXJhIjogeyJpc3N1ZSI6ICJVQ0ItMjMiLCAiaG9zdCI6ICJ2ZXJ3LmJzc24u'\
      'ZXUifX19LCAicGF0aCI6ICIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9y'\
      'aWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5wZGYiLCAidGl0bGUiOiAi'\
      'SG93IHRvIHppcCBkaXJlY3RvcmllcyByZWN1cnNpdmVseSB3aXRoIGhpZGRlbiBmaWxlcyIsICJk'\
      'ZXBzIjogWyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhp'\
      'ZGRlbi1maWxlcyIsICJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13'\
      'aXRoLWhpZGRlbi1maWxlcy9pbWciXX0sIHsiZ2lzdCI6IHsicGF0aCI6ICJob3d0b3MvaG93LXRv'\
      'LXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUubWQi'\
      'LCAiY29tbWl0X2lkIjogImNjYWI0NGUiLCAidGFncyI6IHsiamlyYSI6IHsiaXNzdWUiOiAiVUNC'\
      'LTIzIiwgImhvc3QiOiAidmVydy5ic3NuLmV1In19fSwgInBhdGgiOiAiLmdpc3RvcHMvZGF0YS9o'\
      'b3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxl'\
      'cy9SRUFETUUuamlyYSIsICJ0aXRsZSI6ICJIb3cgdG8gemlwIGRpcmVjdG9yaWVzIHJlY3Vyc2l2'\
      'ZWx5IHdpdGggaGlkZGVuIGZpbGVzIiwgImRlcHMiOiBbImhvd3Rvcy9ob3ctdG8temlwLWRpcmVj'\
      'dG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzIiwgImhvd3Rvcy9ob3ctdG8temlw'\
      'LWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL2ltZyJdfV19Cg=='

    # Base64 encoding of
    # {"semver": "0.1.0-beta", "record-type": "ConvertedGist", "records": [
    # {
    #   "gist": {
    #     "path": "howtos/how-to-setup-a-scalable-vpc-architecture/README.md", 
    #     "commit_id": "ccab44e", 
    #     "tags": {"jira": {"issue": "UCB-22", "host": "verw.bssn.eu"}}
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
    #     "tags": {"jira": {"issue": "UCB-22", "host": "verw.bssn.eu"}}
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
    #     "tags": {"jira": {"issue": "UCB-23", "host": "verw.bssn.eu"}}
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
    #     "tags": {"jira": {"issue": "UCB-23", "host": "verw.bssn.eu"}}
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

        return publishing.JiraAPI(
          url=url, api=FakeJiraApi() )


    mocker.patch('publishing.connect_to_api', side_effect=__connect_to_api)

    main.GistOps(cwd=str(Path.cwd())).run( 
      event_base64=in_base64,
      jira_url='https://verw.bssn.eu/wiki',
      jira_username='unknown',
      jira_password='unknown' )

    assert Path.cwd().joinpath('gistops.trail').exists()
    assert Path.cwd().joinpath('gistops.log').exists()