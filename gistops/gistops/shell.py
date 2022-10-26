#!/usr/bin/env python3
import os
from typing import List
from pathlib import Path
import logging

from invoke.context import Context as InvokeContext


def shrun(
    cmd: List[str],
    cwd: Path,
    env: dict,
    silent_streams: bool = False,
    enforce_absolute_silence: bool = False) -> str:
    """ Runs a command on shell"""
    
    if not enforce_absolute_silence:
        logger = logging.getLogger()
        logger.debug(f'> {" ".join(cmd)}')

    ctx = InvokeContext()
    with ctx.cd(cwd):
        stdout = ctx.run( 
            shell='sh',
            command=" ".join(cmd),
            hide=(silent_streams or enforce_absolute_silence),
            env=env 
        ).stdout

    return stdout
