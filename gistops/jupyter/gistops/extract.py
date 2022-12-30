#!/usr/bin/env python3
"""
use nbconvert to export notebook
"""
import logging
import shutil
from pathlib import Path
from typing import List, Tuple

from traitlets.config import Config
from nbconvert import MarkdownExporter, HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor

import gists


def __render_html(gist: gists.Gist, outdir: Path, launch: bool) -> Tuple[Path, List[str]]:
    # See https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html

    logger = logging.getLogger()
    
    cnf = Config()
    if launch:
        cnf.HTMLExporter.preprocessors = [ExecutePreprocessor]

    exp = HTMLExporter(config=cnf)
    logger.info(f'Export html from {str(gist.path)}')
    (body, _) = exp.from_filename(str(gist.path))

    output_filepath = outdir.joinpath(f'{gist.path.name}.html')
    
    logger.info(f'Write {str(output_filepath)}')
    with open(
      str(output_filepath), 
      mode='w+', encoding='utf-8') as output_file:
        output_file.write(body)

    return output_filepath, []


def __render_markdown(gist: gists.Gist, outdir: Path, launch: bool) -> Tuple[Path, List[str]]:
    # See https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html

    logger = logging.getLogger()

    cnf = Config()
    if launch:
        cnf.MarkdownExporter.preprocessors = [ExecutePreprocessor]

    exp = MarkdownExporter(config=cnf)
    logger.info(f'Export markdown from {str(gist.path)}')
    (body, generated) = exp.from_filename(str(gist.path))

    output_filepath = outdir.joinpath(f'{gist.path.name}.md')
    logger.info(f'Write {str(output_filepath)}')

    with open(
      str(output_filepath), 
      mode='w+', encoding='utf-8') as output_file:
        output_file.write(body)

    resources = []
    for resource_name, resource_data in generated['outputs'].items():
        resource_path = outdir.joinpath(resource_name)
        
        logger.info(f'Write {str(resource_path)}')
        with open( str(resource_path), mode='wb+') as resource_file:
            resource_file.write(resource_data)

        resources.append(f'{str(resource_path.parent)}:{resource_path.name}')

    return output_filepath, resources


def extract(
  gist: gists.Gist, 
  outpath: Path, 
  outformat: str,
  launch: bool) -> gists.Gist:
    '''Extract static report from .ipynb notebook'''

    outdir = outpath.joinpath(gist.path.parent)
    outdir.mkdir(parents=True, exist_ok=True)

    ##########
    # Export #
    ##########
    # See https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html
    nocase_outformat = outformat.lower().strip()
    if nocase_outformat == 'markdown':
        output_filepath, resources = __render_markdown(
          gist=gist, outdir=outdir, launch=launch)
    elif nocase_outformat == 'html':
        output_filepath, resources = __render_html(
          gist=gist, outdir=outdir, launch=launch)
    else:
        raise gists.GistOpsError(
          f'Output format {outformat} is not supported. '
          'Currently supported are only markdown or html')

    ############
    # Copy j2s #
    ############
    if outpath != Path('.'):
        for any_j2_path in sorted(
          list(gist.path.parent.glob('*.j2')), key=str):
            shutil.copy(
              str(any_j2_path),
              str(outdir.joinpath(any_j2_path.name)) )

    return gists.Gist(
      output_filepath,
      gist.commit_id,
      gist.tags,
      resources,
      gist.trace_id,
      gist.title
    )
