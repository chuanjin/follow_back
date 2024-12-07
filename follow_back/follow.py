import requests
import time
import argparse
import os

# GitHub API base URL
BASE_URL = 'https://api.github.com/'

# Headers for authentication
headers = {
    'Authorization': f'token {os.getenv("USER_TOKEN")}',
    'Accept': 'application/vnd.github.v3+json'
}


def get_user_repos(username):
    """Fetch all public repositories of a user."""
    repos = []
    url = f'{BASE_URL}users/{username}/repos'
    page = 1

    while True:
        response = requests.get(url, headers=headers, params={'page': page, 'per_page': 100})
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos

def get_total_stars(username):
    """Calculate the total stars across all repositories of a user."""
    repos = get_user_repos(username)
    total_stars = sum(repo['stargazers_count'] for repo in repos)
    return total_stars


def get_followers(github_username):
    """Fetch the complete list of followers for the specified GitHub user."""
    followers = []
    url = f'{BASE_URL}users/{github_username}/followers'
    page = 1

    while True:
        response = requests.get(url, headers=headers, params={'page': page, 'per_page': 100})
        response.raise_for_status()
        data = response.json()
        
        if not data:
            break
        
        followers.extend(data)
        page += 1

    return followers

def get_following(github_username):
    """Fetch the complete list of users the specified GitHub user is following."""
    following = []
    url = f'{BASE_URL}users/{github_username}/following'
    page = 1

    while True:
        response = requests.get(url, headers=headers, params={'page': page, 'per_page': 100})
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        following.extend(data)
        page += 1

    return following

def get_user_followers_count(username):
    """Fetch the number of followers for a specific user."""
    url = f'{BASE_URL}users/{username}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    user_data = response.json()
    return user_data['followers']

def follow_user(username):
    """Follow a GitHub user."""
    url = f'{BASE_URL}user/following/{username}'
    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        print(f'Successfully followed {username}')
    elif response.status_code == 429:
        print(f'Rate limit exceeded. Pausing...')
        time.sleep(60)  # Wait a minute if rate limited
        follow_user(username)  # Retry following the user
    else:
        print(f'Failed to follow {username}. Status Code: {response.status_code} - {response.text}')


def follow_back(github_username, min_followers, min_stars):
    """Follow back all followers who meet the minimum followers and stars criteria."""
    followers = get_followers(github_username)
    following = get_following(github_username)

    # Normalize usernames to lower case to handle case-sensitivity issues
    followers_usernames = {user['login'].lower() for user in followers}
    following_usernames = {user['login'].lower() for user in following}

    not_following_back = followers_usernames - following_usernames

    for username in not_following_back:
        followers_count = get_user_followers_count(username)
        print(f'{username} has {followers_count} followers.')

        if followers_count >= min_followers:
            total_stars = get_total_stars(username)
            print(f'{username} has {total_stars} total stars.')

            if total_stars >= min_stars:
                follow_user(username)
            else:
                print(f'Skipping {username} (less than {min_stars} stars)')
        else:
            print(f'Skipping {username} (less than {min_followers} followers)')
        
        # Sleep to avoid hitting API rate limits
        time.sleep(1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Follow back your GitHub followers who meet the specified criteria.'
    )
    parser.add_argument('github_username', type=str, help='Your GitHub username.')
    parser.add_argument('min_followers', type=int, help='Minimum number of followers a user must have.')
    parser.add_argument('min_stars', type=int, help='Minimum number of total stars a user must have.')

    args = parser.parse_args()

    follow_back(args.github_username, args.min_followers, args.min_stars)
