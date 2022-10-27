#!/usr/bin/env python3
import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Callable, Iterator
from jsonschema import validate
from jinja2 import Environment, BaseLoader


class GistError(Exception):
    pass


@dataclass
class Gist:
    root: Path
    path: Path
    ops: dict
    

def __load_gist(
    git_root: Path,
    gist_path: Path, 
    gistops_j2: str) -> Gist:
    
    gistops_j2_tmpl = Environment(loader=BaseLoader()).from_string(gistops_j2)
    gistops_str: str = gistops_j2_tmpl.render({
        'root': str(git_root),
        'dir': str(gist_path.parent),
        'file': str(gist_path.name),
        'stem': str(gist_path.stem),
        'suffix': str(gist_path.suffix)
    })
      
    gistops: dict = json.loads(gistops_str)
    validate(instance=gistops, schema={
      "type" : "object",
      "properties" : {
        "type" : {"const":"markdown","description":"Gist type, currently only markdown is supported"},
        "render": {"type":"object","description":"Rendering Configuration"},
        "publish": {"type":"object","description":"Publishing Configuration"}
      },
      "required":["type"]
    })
    
    return Gist(git_root, gist_path, gistops)


def locate_git_root(gist_absolute_path: Path) -> Path:
    """Locates git root directory from gist_path"""
    if not gist_absolute_path.exists():
        raise RuntimeError(f'{gist_absolute_path} does not exist')
        
    def traverse_upwards(gist_path: Path):
        if gist_path.root == gist_path:
            return None
    
        if gist_path.is_dir():
            if len(list(gist_path.glob('.git'))) == 1:
                return gist_path
            
        return traverse_upwards(gist_path.parent)
        
    git_root_path = traverse_upwards(gist_absolute_path.resolve())
    if not git_root_path:
        raise RuntimeError(f'{git_root_path} is not part of a git repository')
    return git_root_path


def iterate_gists(
  shrun: Callable[[List[str],bool], str], 
  git_root: Path,
  gist_path: Path,
  git_diff_hash: str) -> Iterator[Gist]:
    """Locate gists in path using gistops attribute stored in .gitattributes"""
    logger = logging.getLogger()
    
    gist_absolute_path = git_root.joinpath(gist_path).resolve()
    
    git_diff_files: List[Path] = None
    if git_diff_hash is not None:
        git_diff_files = [Path(fc) for fc in shrun(
            cmd=['git','diff-tree','--no-commit-id','--name-only','-r', git_diff_hash]
          ).splitlines()]
          
    if gist_absolute_path.is_dir():
        for gist_absolute_dir in gist_absolute_path.glob('**/'):
            if not gist_absolute_dir.is_dir():
                continue # not a directory
            
            try:
                if gist_absolute_dir.relative_to(git_root.joinpath('.git')):
                    continue # ignore .git sub directory
            except ValueError as _:
                pass
            
            gists_dir = gist_absolute_dir.relative_to(git_root)
            
            # Files with gistops .gitattribute listed as 
            # README.md: gistops: {"pandoc":{"type":"pdf","config":"pandoc.yaml","outfile":"{{file}}.pdf"}}
            # README2.md: gistops: {"pandoc":{"type":"pdf","config":"pandoc.yaml","outfile":"{{file}}.pdf"}}
            for gitattr in shrun(
              cmd=[
                'git','ls-files','|','git','check-attr','-a',
                'gistops',f'{str(gists_dir)}/*.*']).splitlines():
                    
                gist_file, _, gistops_j2 = gitattr.split(': ')
                if git_diff_files is not None and \
                    Path(gist_file) not in git_diff_files:
                    logger.info(f'{gist_file} unchanged for {git_diff_hash}')
                    continue
                    
                yield __load_gist(
                    git_root=git_root,
                    gist_path=Path(gist_file),
                    gistops_j2=gistops_j2 )
                    
                
                
    elif gist_absolute_path.is_file():
        gitattr = shrun(cmd=['git','check-attr','gistops', str(gist_path)])
        if gitattr != '': 
            gist_file, _, gistops_j2 = gitattr.split(' ')
            if git_diff_files is None or \
                Path(gist_file) in git_diff_files:    
                
                yield __load_gist(
                git_root=git_root,
                gist_path=gist_absolute_dir.relative_to(
                  git_root).joinpath(gist_file),
                gistops_j2=gistops_j2 )
            
                
    else:
        raise RuntimeError(
            f'{gist_path} is symbolic link. '
            'Symbolic links are not supported.'
            'Please provide file or directory')
            
        
