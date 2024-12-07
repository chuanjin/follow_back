# Follow Back Bot

This is a Python script that automatically follows back your GitHub followers who meet the specified criteria. The script leverages the GitHub API to fetch your followers, check their follower counts, public repositories total stars, and then follow them back if they meet the criteria. The script will be triggered in Github Actions by a nightly build configured with cron.

## Features

- **Automatic Follow Back**: Automatically follow back your GitHub followers based on their follower count.
- **Customizable Threshold**: Set a minimum follower count and minimum total starts to control which followers get followed back.
- **Handles API Rate Limiting**: The script handles GitHub's API rate limiting to ensure compliance with GitHub's usage policies.
- **Pagination Handling**: The script retrieves all followers and following users, regardless of their count, by handling pagination.
- **Case-Insensitive Matching**: The script matches followers and following users in a case-insensitive manner to prevent issues.

## Requirements

- Python 3.x
- Poetry (for dependency management)
- A GitHub Personal Access Token with `follow` scope enabled (Settings -> Developer Settings -> Personal access tokens -> Tokens)

## Installation

1. **Clone the Repository**:

2. **Install Poetry** (if not already installed):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
3. **Install dependencies**:

   ```bash
   poetry install
4. **Set Up Environment Variables**:

   And ensure the PAT has the following permissions:
   - read:user
   - user:follow

   Create a .env file in the project root or export the GitHub token directly in your environment:

   ```bash
   export USER_TOKEN=your_personal_access_token


## Usage

You can run the script manually by providing your GitHub username, the minimum number of followers and the minimum total stars required for a follow-back:

```bash
poetry run python follow_back/follow.py your_github_username 100 100
