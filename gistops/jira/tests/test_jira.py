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
    
    in_base64 = 'eyJzZW12ZXIiOiIwLjEuMC1iZXRhIiwicmVjb3JkLXR5cGUiOiJHaXN0IiwicmVjb3JkcyI6W3sicGF0aCI6Ii5naXN0b3BzL2RhdGEvaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLnBkZiIsInRhZ3MiOnsiamlyYSI6eyJpc3N1ZSI6IlVDQi0yMiIsImhvc3QiOiJ2ZXJ3LmJzc24uZXUifX0sImNvbW1pdF9pZCI6IjA0MTkzYWQiLCJyZXNvdXJjZXMiOlsiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmU6KiIsImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL2ltZzoqIl0sInRyYWNlX2lkIjoiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLm1kIiwidGl0bGUiOiJIb3cgdG8gc2V0dXAgYSBzY2FsYWJsZSB2cGMgYXJjaGl0ZWN0dXJlIn0seyJwYXRoIjoiLmdpc3RvcHMvZGF0YS9ob3d0b3MvaG93LXRvLXNldHVwLWEtc2NhbGFibGUtdnBjLWFyY2hpdGVjdHVyZS9SRUFETUUuamlyYSIsInRhZ3MiOnsiamlyYSI6eyJpc3N1ZSI6IlVDQi0yMiIsImhvc3QiOiJ2ZXJ3LmJzc24uZXUifX0sImNvbW1pdF9pZCI6IjA0MTkzYWQiLCJyZXNvdXJjZXMiOlsiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmU6KiIsImhvd3Rvcy9ob3ctdG8tc2V0dXAtYS1zY2FsYWJsZS12cGMtYXJjaGl0ZWN0dXJlL2ltZzoqIl0sInRyYWNlX2lkIjoiaG93dG9zL2hvdy10by1zZXR1cC1hLXNjYWxhYmxlLXZwYy1hcmNoaXRlY3R1cmUvUkVBRE1FLm1kIiwidGl0bGUiOiJIb3cgdG8gc2V0dXAgYSBzY2FsYWJsZSB2cGMgYXJjaGl0ZWN0dXJlIn0seyJwYXRoIjoiLmdpc3RvcHMvZGF0YS9ob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUucGRmIiwidGFncyI6eyJqaXJhIjp7Imlzc3VlIjoiVUNCLTIzIiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiMDQxOTNhZCIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlczoqIiwiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvaW1nOioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUubWQiLCJ0aXRsZSI6IkhvdyB0byB6aXAgZGlyZWN0b3JpZXMgcmVjdXJzaXZlbHkgd2l0aCBoaWRkZW4gZmlsZXMifSx7InBhdGgiOiIuZ2lzdG9wcy9kYXRhL2hvd3Rvcy9ob3ctdG8temlwLWRpcmVjdG9yaWVzLXJlY3Vyc2l2ZWx5LXdpdGgtaGlkZGVuLWZpbGVzL1JFQURNRS5qaXJhIiwidGFncyI6eyJqaXJhIjp7Imlzc3VlIjoiVUNCLTIzIiwiaG9zdCI6InZlcncuYnNzbi5ldSJ9fSwiY29tbWl0X2lkIjoiMDQxOTNhZCIsInJlc291cmNlcyI6WyJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlczoqIiwiaG93dG9zL2hvdy10by16aXAtZGlyZWN0b3JpZXMtcmVjdXJzaXZlbHktd2l0aC1oaWRkZW4tZmlsZXMvaW1nOioiXSwidHJhY2VfaWQiOiJob3d0b3MvaG93LXRvLXppcC1kaXJlY3Rvcmllcy1yZWN1cnNpdmVseS13aXRoLWhpZGRlbi1maWxlcy9SRUFETUUubWQiLCJ0aXRsZSI6IkhvdyB0byB6aXAgZGlyZWN0b3JpZXMgcmVjdXJzaXZlbHkgd2l0aCBoaWRkZW4gZmlsZXMifV19'
    # Base64 encoding of ... {"semver":"0.1.0-beta","record-type":"Gist","records":[{"path":".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.pdf","tags":{"jira":{"issue":"UCB-22","host":"verw.bssn.eu"}},"commit_id":"04193ad","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:*","howtos/how-to-setup-a-scalable-vpc-architecture/img:*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"How to setup a scalable vpc architecture"},{"path":".gistops/data/howtos/how-to-setup-a-scalable-vpc-architecture/README.jira","tags":{"jira":{"issue":"UCB-22","host":"verw.bssn.eu"}},"commit_id":"04193ad","resources":["howtos/how-to-setup-a-scalable-vpc-architecture:*","howtos/how-to-setup-a-scalable-vpc-architecture/img:*"],"trace_id":"howtos/how-to-setup-a-scalable-vpc-architecture/README.md","title":"How to setup a scalable vpc architecture"},{"path":".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.pdf","tags":{"jira":{"issue":"UCB-23","host":"verw.bssn.eu"}},"commit_id":"04193ad","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:*","howtos/how-to-zip-directories-recursively-with-hidden-files/img:*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"How to zip directories recursively with hidden files"},{"path":".gistops/data/howtos/how-to-zip-directories-recursively-with-hidden-files/README.jira","tags":{"jira":{"issue":"UCB-23","host":"verw.bssn.eu"}},"commit_id":"04193ad","resources":["howtos/how-to-zip-directories-recursively-with-hidden-files:*","howtos/how-to-zip-directories-recursively-with-hidden-files/img:*"],"trace_id":"howtos/how-to-zip-directories-recursively-with-hidden-files/README.md","title":"How to zip directories recursively with hidden files"}]}
    
    def __connect_to_api( url: str, access_token: str ):
        assert access_token == 'unknown'

        return publishing.JiraAPI(
          url=url, api=FakeJiraApi() )

    mocker.patch('publishing.connect_to_api', side_effect=__connect_to_api)

    main.GistOps(cwd=str(Path.cwd())).run( 
      event_base64=in_base64,
      jira_url='https://verw.bssn.eu/wiki',
      jira_access_token='unknown')

    assert Path.cwd().joinpath('.gistops').joinpath('jira.gistops.trail').exists()
    assert Path.cwd().joinpath('.gistops').joinpath('jira.gistops.log').exists()