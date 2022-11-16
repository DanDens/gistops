#!/usr/bin/env python3
"""
Create Traillogs HTML Representation
"""
from typing import List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import logging

import gists


@dataclass
class TrailLog:
    """ Gistops Trail Representation """
    operation: str
    level: int
    time: datetime
    gist: Path
    action: str


def from_file(gistops_trail_path: Path) -> List[TrailLog]:
    """Deserializes traillogs from file"""

    with open(gistops_trail_path, 'r', encoding='utf-8') as gistops_trail_file:
        gistops_trail = gistops_trail_file.read()

    traillogs: List[TrailLog] = list()
    for trail in gistops_trail.splitlines():
        operation_str, level_str, time_str, gist_str, action_str = trail.split(',')

        def __name_to_level(level: str):
            match level:
                case 'CRITICAL': return logging.CRITICAL
                case 'FATAL': return logging.FATAL
                case 'ERROR': return logging.ERROR
                case 'WARN': return logging.WARNING
                case 'WARNING': return logging.WARNING
                case 'INFO': return logging.INFO
                case 'DEBUG': return logging.DEBUG
                case 'NOTSET': return logging.NOTSET
                case _: 
                    raise gists.GistOpsError(
                      'Unknown traillog level {level}, '
                      'must be one of [CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET')

        traillogs.append(TrailLog(
          operation=operation_str,
          level=__name_to_level(level_str),
          time=datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ'),
          gist=Path(gist_str),
          action=action_str ))
    return traillogs


def max_severity(traillogs: List[TrailLog]) -> int:
    """Returns the maximum severity found in the traillogs"""
    if len(traillogs) == 0:
        return logging.NOTSET
        
    max_trail: TrailLog = max(traillogs, key=lambda trail: trail.level)
    return max_trail.level
