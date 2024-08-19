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

def get_followers(github_username):
    """Fetch the list of followers for the specified GitHub user."""
    url = f'{BASE_URL}users/{github_username}/followers'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_following(github_username):
    """Fetch the list of users the specified GitHub user is following."""
    url = f'{BASE_URL}users/{github_username}/following'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

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
    else:
        print(f'Failed to follow {username}. Status Code: {response.status_code}')

def follow_back(github_username, min_followers):
    """Follow back all followers who meet the minimum followers criteria."""
    followers = get_followers(github_username)
    following = get_following(github_username)

    followers_usernames = {user['login'] for user in followers}
    following_usernames = {user['login'] for user in following}

    not_following_back = followers_usernames - following_usernames

    for username in not_following_back:
        followers_count = get_user_followers_count(username)
        print(f'{username} has {followers_count} followers.')
        
        if followers_count > min_followers:
            follow_user(username)
        else:
            print(f'Skipping {username} (less than {min_followers} followers)')
        
        # Sleep to avoid hitting API rate limits
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Follow back your GitHub followers who have more than a specified number of followers.')
    parser.add_argument('github_username', type=str, help='Your GitHub username.')
    parser.add_argument('min_followers', type=int, help='Minimum number of followers a user must have to be followed back.')

    args = parser.parse_args()

    follow_back(args.github_username, args.min_followers)