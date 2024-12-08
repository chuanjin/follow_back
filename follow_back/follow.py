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


def fetch_paginated_data(url, params=None):
    """
    Fetch data from a paginated API endpoint with rate limit handling.
    """
    data = []
    page = 1
    while True:
        response = requests.get(url, headers=headers, params={**(params or {}), 'page': page, 'per_page': 100})
        
        if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            sleep_duration = reset_time - int(time.time())
            print(f"Rate limit reached. Sleeping for {sleep_duration} seconds...")
            time.sleep(sleep_duration)
            continue  # Retry the same request
        
        response.raise_for_status()
        
        # Check remaining rate limit
        remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
        if remaining == 0:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            sleep_duration = reset_time - int(time.time())
            print(f"Rate limit will reset in {sleep_duration} seconds. Pausing...")
            time.sleep(sleep_duration)
        
        page_data = response.json()
        if not page_data:
            break
        
        data.extend(page_data)
        page += 1

    return data


def get_user_repos(username):
    """Fetch all public repositories of a user."""
    url = f'{BASE_URL}users/{username}/repos'
    return fetch_paginated_data(url)


def get_followers(username):
    """Fetch the complete list of followers for the specified GitHub user."""
    url = f'{BASE_URL}users/{username}/followers'
    return fetch_paginated_data(url)


def get_following(username):
    """Fetch the complete list of users the specified GitHub user is following."""
    url = f'{BASE_URL}users/{username}/following'
    return fetch_paginated_data(url)


def get_user_followers_count(username):
    """Fetch the number of followers for a specific user."""
    url = f'{BASE_URL}users/{username}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['followers']


def get_total_stars(username):
    """Calculate the total stars across all repositories of a user."""
    repos = get_user_repos(username)
    return sum(repo['stargazers_count'] for repo in repos)


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
