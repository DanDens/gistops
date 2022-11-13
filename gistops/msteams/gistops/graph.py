#!/usr/bin/env python3
"""
Create Graph-Representation from Gists
"""
from typing import List
from pathlib import Path

import networkx as nx

import gists


def as_graph(gsts: List[gists.Gist]) -> nx.Graph:
    """Computes a graph from gists"""
    gists_graph = nx.Graph()
    return gists_graph
