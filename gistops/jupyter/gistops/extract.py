#!/usr/bin/env python3
"""
use nbconvert to export notebook
"""
import logging
import shutil
from pathlib import Path
from typing import List, Tuple, Any
from functools import wraps

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from traitlets.config import Config
from nbconvert import MarkdownExporter, HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor

import gists


def __render_html(
  gist: gists.Gist, 
  outdir: Path, 
  outtemplate: Path,
  launch: bool) -> Tuple[Path, List[str]]:
    logger = logging.getLogger()
    
    cnf = Config()
    if launch:
        cnf.HTMLExporter.preprocessors = [ExecutePreprocessor]

    if outtemplate is not None:
        cnf.HTMLExporter.extra_template_basedirs = [str(outtemplate.parent)]
        cnf.HTMLExporter.template_name = outtemplate.name

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


def __render_markdown(
  gist: gists.Gist,
  outdir: Path,
  outtemplate: Path,
  launch: bool) -> Tuple[Path, List[str]]:
    logger = logging.getLogger()

    cnf = Config()
    if launch:
        cnf.MarkdownExporter.preprocessors = [ExecutePreprocessor]

    if outtemplate is not None:
        cnf.MarkdownExporter.extra_template_basedirs = [str(outtemplate.parent)]
        cnf.MarkdownExporter.template_name = outtemplate.name

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


def __tagged(tag_name: str):
    def inner_tagged(func):
        @wraps(func)
        def decorator_func(*args, **kwargs) -> Any:

            gist: gists.Gist = \
                args[0] if len(args) > 0 else kwargs['gist']

            if tag_name in gist.tags:
                try:
                    validate(instance=gist.tags[tag_name], schema={
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "format": {"type": "string"},
                                "template": {"type": "string"},
                                "launch": {"type": "boolean"}
                            },
                            "required": ["format"]
                        }
                    })
                except ValidationError as err:
                    raise gists.GistOpsError(
                      f'Schema validation failed for tag {tag_name}') from err
                
                if 'template' in gist.tags[tag_name]: 
                    
                    template_path = Path(gist.tags[tag_name]['template']).joinpath('conf.json')

                    if not Path(gist.tags[tag_name]['template']).exists() and \
                      not gist.path.parent.joinpath(gist.tags[tag_name]['template']).exists():
                        raise gists.GistOpsError(
                          f'Template for {gist.path} does not exist')

                    try:
                        template_path.resolve().relative_to(Path('.').resolve())
                    except ValueError as err:
                        raise gists.GistOpsError(
                          f'Template {template_path} must be relative to git root') from err


            return func(*args, **kwargs)

        return decorator_func
    return inner_tagged


@__tagged('jupyter')
def extract(
  gist: gists.Gist, 
  outpath: Path) -> List[gists.Gist]:
    '''Extract static report from .ipynb notebook'''

    outdir = outpath.joinpath(gist.path.parent)
    outdir.mkdir(parents=True, exist_ok=True)

    nbconverts: List[dict] = []
    if 'jupyter' in gist.tags:
        nbconverts = gist.tags['jupyter']
    else:
        nbconverts = [{'format': 'markdown'}]

    gsts: List[gists.Gist] = []
    for nbconvert in nbconverts:
        ##########
        # Export #
        ##########
        # See https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html
        # and https://nbconvert.readthedocs.io/en/latest/api/index.html

        nbconvert_template: Path = None
        if 'template' in nbconvert:
            conv_json_path = Path(nbconvert['template']).joinpath('conf.json')
            if conv_json_path.exists():
                nbconvert_template = Path( nbconvert['template'] )

            elif gist.path.parent.joinpath(conv_json_path).exists():
                nbconvert_template = gist.path.parent.joinpath(nbconvert['template'])

        nocase_outformat = nbconvert['format'].lower().strip()
        if nocase_outformat == 'markdown':
            output_filepath, resources = __render_markdown(
              gist = gist,
              outdir = outdir,
              outtemplate = nbconvert_template, 
              launch = nbconvert['launch'] if 'launch' in nbconvert else False)
        
        elif nocase_outformat == 'html':
            output_filepath, resources = __render_html(
              gist = gist,
              outdir = outdir,
              outtemplate = nbconvert_template,
              launch = nbconvert['launch'] if 'launch' in nbconvert else False)
        
        else:
            raise gists.GistOpsError(
              f'Output format {nbconvert["format"]} is not supported. '
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

        gsts.append( gists.Gist(
          output_filepath,
          gist.commit_id,
          gist.tags,
          resources,
          gist.trace_id,
          gist.title) )
    return gsts
