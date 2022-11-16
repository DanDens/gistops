#!/usr/bin/env python3
"""
Tests for git-ls-attr gistops image
"""
import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from typing import List
from jsonschema import validate

import pytest
from bs4 import BeautifulSoup

sys.path.append(
  str(Path(os.path.realpath(__file__)).parent.parent.joinpath('gistops')))

import main
import reporting
import gists


@pytest.fixture(scope="module", autouse=True)
def extract_msteams_repository():
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


class FakeMsTeamsWebhookApi:
    """ Replaces actual MsTeams Webhook API for testing """
    def __init__(self):
        self.soup = None

    def send(self, message_card: str):
        """Check POST request to msteams webhook is correct"""

        msg = json.loads(message_card)
        validate(instance=msg, schema={
          'type': 'object',
          'properties': {
            '@context': {'const': 'https://schema.org/extensions'},
            '@type': {'const': 'MessageCard'},
            'themeColor': {'type': 'string'},
            'title': {'const': 'trails from the test'},
            'text': {'type': 'string'}
          },
          'required': ['@context','@type','themeColor','title','text']
        })

        self.soup = BeautifulSoup(f'<html><body>{msg["text"]}</body></html>', 'html.parser')
        assert bool(self.soup.find()) # is it valid html?


def test_example_repo(mocker):
    """Tests reporting with small example"""

    ################
    # Mock msteams #
    ################
    fk_api = FakeMsTeamsWebhookApi()

    def __to_fake_webhook_api(_: str) -> FakeMsTeamsWebhookApi:
        """Create fake webhook api from url"""
        return fk_api

    ###############
    # Run msteams #
    ###############
    mocker.patch('reporting.to_webhook_api', side_effect=__to_fake_webhook_api)

    main.GistOps( cwd=str(Path.cwd()) ).run( 
      webhook_url='https://not-a-real-webhook',
      report_title='trails from the test' )

    assert Path.cwd().joinpath('gistops.log').exists()

    ###############
    # Test output #
    ###############
    def __ensure_td_class_keywords(
      soup: BeautifulSoup, td_class: str, num:int, keywords: List[str]):
        tds = soup.find_all('td', {'class': td_class})
        assert len(tds) == num

        for this_td in tds:
            for keyword in keywords:
                if this_td.text.find(keyword) >= 0:
                    break
            else:
                assert False

    __ensure_td_class_keywords(
      fk_api.soup, 'operation', 2, [
      'how-to-setup-a-scalable-vpc-architecture', 
      'how-to-zip-directories-recursively-with-hidden-files'])

    __ensure_td_class_keywords(
      fk_api.soup, 'action', 2, ['confluence', 'git-ls-attr', 'jira', 'pandoc'])


def test_no_changes():
    """Tests msteams reporting with no changes"""

    ################
    # Mock msteams #
    ################
    fk_api = FakeMsTeamsWebhookApi()

    reporting.report(
          webhook_api = fk_api, 
          report_title='trails from the test',
          gsts=gists.from_file(gists_json_path=Path.cwd().joinpath('gists.json')), 
          traillogs=[] )
