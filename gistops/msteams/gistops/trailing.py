#!/usr/bin/env python3
"""
Create Graph-Representation from Gists
"""
from typing import List
from pathlib import Path
from collections import Counter
from datetime import datetime
from dataclasses import dataclass

import networkx as nx

import gists


@dataclass
class Trail:
    """ Gistops Trail Representation """
    module: str
    type: str
    time: datetime
    gist: Path
    action: str


def __as_graph(gsts: List[gists.Gist], trails: List[Trail]) -> nx.Graph:
    """Computes a graph from gistops traillog using gists as nodes"""
    nxg = nx.Graph()

    #############
    # Add Gists #
    #############
    for gist in gsts:
        nxg.add_node(gist.path)

    ###################
    # Shared Prefixes #
    ###################
    # Count common path prefixes
    cnt = Counter()
    for gist in gsts:
        cnt.update(gist.path.parents)

    # Filter path prefixes which are not shared by gists
    shared_prefixes = [prefix for prefix, count in cnt.items() if count > 1]
    shared_prefixes = sorted(shared_prefixes, key= lambda prefix : len(str(prefix)), reverse=True)

    # Add shared path prefixes as nodes
    for prefix in shared_prefixes:
        nxg.add_node( prefix )
    
    #################
    # Connect Gists #
    #################
    for gist in gsts:
        for prefix in shared_prefixes:
            try:
                gist.path.relative_to(prefix)
                # Connect Gist to prefix
                nxg.add_edge( prefix, gist.path )
                 
                break
            except ValueError:
                pass
    return nxg


def to_html(gsts: List[gists.Gist], gistops_trail_path: Path) -> str:
    """Renders a html from trailing information"""
    
    with open(gistops_trail_path, 'r', encoding='utf-8') as gistops_trail_file:
        gistops_trail = gistops_trail_file.read()

    trails: List[Trail] = list()
    for trail in gistops_trail.splitlines():
        module_str, type_str, time_str, gist_str, action_str = trail.split(',')

        trails.append(Trail(
          module=module_str,
          type=type_str,
          time=datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ'),
          gist=Path(gist_str),
          action=action_str
        ))

    nxg = __as_graph(gsts=gsts, trails=trails)