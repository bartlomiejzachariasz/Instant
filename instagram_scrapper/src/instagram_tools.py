from instagram_scrapper.src.request_tools import simple_get, get_json
from bs4 import BeautifulSoup
import re
import json


def get_user_data(username):
    instagram_url = 'https://www.instagram.com/{0}/?hl=en'.format(username)
    raw_html = simple_get(instagram_url)
    html = BeautifulSoup(raw_html, 'html.parser')
    data = ''
    for script in html.select('script'):
        if script['type'] == 'application/ld+json':
            data = script.text
    followers = re.search(r'userInteractionCount\"\:\"(\d+)\"', data).group()
    followers = ''.join([s for s in followers if s.isdigit()])
    print(int(followers))


def get_data_from_tags(tag):
    instagram_url = 'https://www.instagram.com/explore/tags/{0}/'.format(tag)
    raw_html = simple_get(instagram_url)
    html = BeautifulSoup(raw_html, 'html.parser')
    data = prepare_data(html)
    for row in data:
        username, followers = get_username_by_id(extract_user_id(row))
        single_photo = {'tags': extract_tags(row), 'likes': extract_likes(row), 'date': extract_date(row),
                        'photo_url': extract_photo_url(row), 'username' : username, 'followers' : followers}
        print(single_photo)
        break


def get_username_by_id(id):
    instagram_url = 'https://i.instagram.com/api/v1/users/{0}/info/'.format(id)
    raw_data = get_json(instagram_url)
    json_data = json.loads(raw_data)
    followers = json_data['user']['follower_count']
    username = json_data['user']['username']
    return username, followers


def extract_date(content):
    date = re.search(r'\"taken_at_timestamp\"\:(\d)+', content).group()
    return date.split(':')[1]


def extract_photo_url(content):
    photo_url = re.search(
        r'\"config\_width\"\:480\,\"config\_height\"\:480\}\,\{\"src\"\:\"(.)+\"\,\"config\_width\"\:640',
        content).group()
    return re.findall(r'(https?://[^\s]+)\"\,', photo_url)


def extract_user_id(content):
    user_id = re.search(r'\"owner\"\:\{\"id\"\:\"(\d)+', content).group()
    return user_id.split("\"")[-1]


def extract_likes(content):
    likes = re.search(r'\"edge_liked_by\"\:\{\"count\"\:(\d)+', content).group()
    return likes.split(':')[2]


def extract_tags(content):
    description = re.search(r'\"text\"\:\"(.)+\"\}\}\]\}', content).group()
    return re.findall(r"#(\w+)", description)


def prepare_data(html):
    data = ''
    for script in html.select('script'):
        if script['type'] == 'text/javascript':
            m = re.search(r'^(window\._sharedData)', script.text)
            if m:
                data = script.text
    data = data.split('[{"node":')
    data.remove(data[0])
    data.remove(data[0])
    return data
