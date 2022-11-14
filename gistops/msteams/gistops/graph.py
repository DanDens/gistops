#!/usr/bin/env python3
"""
Create Graph-Representation from Gists
"""
from typing import List
from pathlib import Path
from collections import Counter

import networkx as nx

import gists


def as_graph(gsts: List[gists.Gist]) -> nx.Graph:
    """Computes a graph from gists"""
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
