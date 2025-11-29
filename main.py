from github_connector_project.client import GitHubClient
from github_connector_project.logger import setup_logger
from dotenv import load_dotenv
from pprint import pprint
import os

load_dotenv()

# Setting up my logger
logger = setup_logger(__name__)

git_token = os.getenv("GIT_PAT_KEY")
# git_token = "AFSJKGUEkmlfjawuiej"


OWNER = "vinta"
REPO = "awesome-python"


def main():
    try:
        gitClient = GitHubClient(token = git_token)
        repo_details = gitClient.get_repo_details(OWNER, REPO)
        pprint(repo_details)
    except Exception as e:
        logger.error(f"An error occured: {e}")

if __name__ == "__main__":
    main()