import os
import sys
import logging
from subprocess import run as srun
from os import path as ospath
from os import execl as osexecl
from os import getenv
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def update_from_upstream():
    if os.path.exists('config.env'):
        load_dotenv('config.env')

    UPSTREAM_REPO = getenv("UPSTREAM_REPO")
    UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH")
    UPSTREAM_TOKEN = getenv("ACCESS_TOKEN")

    if not UPSTREAM_REPO:
        logger.info("No UPSTREAM_REPO in config.env → skipping update")
        return False

    repo_url = UPSTREAM_REPO
    if UPSTREAM_TOKEN:
        if "github.com" in repo_url:
            repo_url = repo_url.replace("https://", f"https://{UPSTREAM_TOKEN}@")

    logger.info(f"Updating from: {repo_url}  ({UPSTREAM_BRANCH})")

    try:
        if ospath.exists('.git'):
            srun(["rm", "-rf", ".git"], check=True)

        cmd = (
            "git init -q "
            "&& git add . "
            "&& git commit -sm 'temp update commit' -q "
            "&& git remote add origin " + repo_url + " "
            "&& git fetch origin -q "
            "&& git reset --hard origin/" + UPSTREAM_BRANCH + " -q"
        )

        result = srun(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Update successful → restarting")
            osexecl(sys.executable, sys.executable, "-m", "VideoEncoder")
            # ↑ process is replaced — code below never runs
        else:
            logger.error("Update failed")
            logger.error(result.stderr)
            return False

    except Exception as e:
        logger.exception(f"Update crashed: {e}")
        return False

    return False
