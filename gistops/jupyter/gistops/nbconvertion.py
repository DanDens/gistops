#!/usr/bin/env python3
"""
use nbconvert to export notebook
"""
import logging
from pathlib import Path
import shutil

import nbformat
from nbconvert import HTMLExporter

import gists


def convert(gist: gists.Gist, outpath: Path) -> gists.Gist:
    '''Convert .ipynb to .html using nbconvert'''
    logger = logging.getLogger()

    # See https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html

    #################
    # Read Notebook #
    #################
    logger.info(f'Open notebook {str(gist.path)}')
    with open(file=str(gist.path), mode='r', encoding='utf-8') as notebook_file:
        notebook = nbformat.reads(notebook_file.read(), as_version=4)

    ###################
    # Export Notebook #
    ###################
    logger.info(f'Render static html for notebook {str(gist.path)}')
    # create the new exporter using the custom config
    html_exporter = HTMLExporter(template_name='classic')
    (html_body, _) = html_exporter.from_notebook_node(notebook)

    ##############
    # Write Html #
    ##############
    output_filepath = outpath.joinpath(gist.path.parent).joinpath(
          f'{gist.path.name}.html')
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f'Write static html from {str(gist.path)} to {str(output_filepath)}')

    with open(
      str(output_filepath), 
      mode='w+', encoding='utf-8') as output_file:
        output_file.write(html_body)

    ############
    # Copy j2s #
    ############
    if outpath != Path('.'):
        for any_j2_path in sorted(
          list(gist.path.parent.glob('*.j2')), key=str):
            shutil.copy(
              str(any_j2_path),
              str(outpath.joinpath(
                any_j2_path.parent).joinpath(any_j2_path.name)) )

    return gists.Gist(
      output_filepath,
      gist.commit_id,
      gist.tags
    )
