#!/usr/bin/env python3
import os
from typing import List
from pathlib import Path
import logging

from invoke import run as __shell


def shell(
    cmd: List[str],
    enforce_silent: bool,
    cwd: Path,
    env: dict,
    silent_cmd: bool,
    silent_run: bool) -> str:
    """ Runs a command on shell"""
    if not silent_cmd and not enforce_silent:
        logger = logging.getLogger()
        logger.info(" ".join(cmd))

    old_cwd = Path.cwd()
    try:
        if Path.cwd() != cwd:
            os.chdir(str(cwd))
        stdout = __shell(
            shell='sh',
            command=" ".join(cmd),
            hide=(silent_run or enforce_silent),
            env=env).stdout
    except Exception as err:
        raise err
    finally:
        if Path.cwd() != old_cwd:
            os.chdir(str(old_cwd))

    return stdout
