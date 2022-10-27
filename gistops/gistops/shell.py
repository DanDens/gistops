#!/usr/bin/env python3
"""
Functions to execute commands on the shell
"""
from typing import List
from pathlib import Path
import logging

from invoke.context import Context as InvokeContext
from invoke.exceptions import UnexpectedExit


class ShellError(Exception):
    """Error from shell in case exit code is not 0"""


def shrun(
    cmd: List[str],
    cwd: Path,
    env: dict,
    log_cmd_level: int = logging.DEBUG,
    hide_streams: bool = False,
    enforce_absolute_silence: bool = False,
    do_not_execute: bool = False) -> str:
    """ Runs a command on shell"""
    
    if not enforce_absolute_silence:
        logger = logging.getLogger()
        logger.log(log_cmd_level,f'> {" ".join(cmd)}')

    if do_not_execute:
        return '' # Do nothing, please ... it is a dry run
    try:
        ctx = InvokeContext()
        with ctx.cd(cwd):
            stdout = ctx.run( 
                shell='sh',
                command=" ".join(cmd),
                hide=(hide_streams or enforce_absolute_silence),
                env=env 
            ).stdout
    except UnexpectedExit as err:
        raise ShellError("unexpected exit") from err

    return stdout
