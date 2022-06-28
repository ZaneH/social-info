#!/usr/bin/env python3
"""Social Info

Usage:
    social_info.py instagram followers <user_id> [--inspect | --load-cursor] [<output>]
    social_info.py twitter followers <user_id> [--inspect | --load-cursor] [<output>]
    social_info.py tiktok followers <user_id> [--inspect | --load-cursor] [<output>]
    social_info.py (-h | --help)

Options:
    --load-cursor       Load cursors from save data (recommended if you're picking up a previous session)
    -i --inspect        Show the available dictionary keys within a response (won't save output)
    -h --help           Show this message

"""

from time import sleep
from docopt import docopt
from instagram_private_api import Client, ClientCookieExpiredError, ClientLoginRequiredError, ClientLoginError, ClientError
from instagram_private_api_extensions import pagination
import tweepy
import json, os, codecs, csv, requests
from dotenv import load_dotenv
from mapping import Mapping

load_dotenv('./env.secret')

settings = {
    'insta_api': {},
    'twitter_cursors': {},
    'insta_cursors': {},
    'tiktok_cursors': {}
}


# helper functions
def update_settings_file():
    with open(settings_file, 'w') as outfile:
        json.dump(settings, outfile, default=to_json)
        print('Data saved: {0!s}'.format(settings_file))


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {
            '__class__': 'bytes',
            '__value__': codecs.encode(python_object, 'base64').decode()
        }
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    settings['insta_api'] = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(settings, outfile, default=to_json)
        print('Data saved: {0!s}'.format(new_settings_file))


instagram_username = os.getenv('INSTAGRAM_USERNAME')
instagram_password = os.getenv('INSTAGRAM_PASSWORD')
twitter_bearer = os.getenv('TWITTER_BEARER')
settings_file = './session-data.tmp'
device_id = None
tiktok_api_url = 'https://scraptik.p.rapidapi.com/list-followers'

# setup settings & instagram client
try:
    if not os.path.isfile(settings_file):
        print('No settings found, creating a session file...')

        instapi = Client(instagram_username,
                         instagram_password,
                         on_login=lambda x: onlogin_callback(x, settings_file))
    else:
        # load settings
        with open(settings_file) as file_data:
            settings = json.load(file_data, object_hook=from_json)
        print('Found save data: {0!s}'.format(settings_file))

        device_id = settings['insta_api'].get('device_id')
        instapi = Client(instagram_username,
                         instagram_password,
                         settings=settings['insta_api'])
except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
    print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

    # login expired, re-login
    instapi = Client(instagram_username,
                     instagram_password,
                     device_id=device_id,
                     on_login=lambda x: onlogin_callback(x, settings_file))

except ClientLoginError as e:
    print('ClientLoginError {0!s}'.format(e))
    exit(9)
except ClientError as e:
    print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(
        e.msg, e.code, e.error_response))
    exit(9)
except Exception as e:
    print('Unexpected Exception: {0!s}'.format(e))
    exit(99)

# setup twitter client
try:
    twitter_api = tweepy.Client(twitter_bearer, wait_on_rate_limit=True)
except:
    print("Error signing into Twitter")


# save insta followers to csv with auto-retry
def get_insta_followers(cooldown=60):
    try:
        followers = []
        current = 0
        chunk_size = 5

        args = {
            'user_id': opts['<user_id>'],
            'rank_token': Client.generate_uuid(),
        }

        # load cursor from save if needed
        if settings['insta_cursors'].get(
                'next_max_id') and opts['--load-cursor']:
            args['max_id'] = settings['insta_cursors']['next_max_id']

        for results in pagination.page(instapi.user_followers, args=args):
            current += 1
            args['max_id'] = results['next_max_id']

            print("Scraping page:\t{0}\nnext_max_id:\t{1}\n".format(
                current, results['next_max_id']))

            if results.get('users'):
                followers.extend(results['users'])

            if current % chunk_size == 0:
                print('Grabbing user data. This will take a minute...')
                # get more data on each instagram user
                follower_metrics = {}
                for f in followers:
                    follower_resp = instapi.user_info(f['pk'])
                    data = follower_resp['user']
                    follower_metrics[f['pk']] = {}
                    if data.get('follower_count'):
                        follower_metrics[
                            f['pk']]['follower_count'] = data['follower_count']
                    if data.get('following_count'):
                        follower_metrics[f['pk']]['following_count'] = data[
                            'following_count']
                    if data.get('mutual_followers_count'):
                        follower_metrics[
                            f['pk']]['mutual_followers_count'] = data[
                                'mutual_followers_count']
                    if data.get('is_new_to_instagram'):
                        follower_metrics[
                            f['pk']]['is_new_to_instagram'] = data[
                                'is_new_to_instagram']

                    sleep(1)

                settings['insta_cursors'] = {'next_max_id': args['max_id']}
                update_settings_file()
                # write to file or print
                if not is_inspecting:
                    new_file = not os.path.isfile(opts['<output>'])
                    with open(opts['<output>'], 'a', encoding='UTF8') as f:
                        headers = Mapping.aggregate_field_names(followers)
                        headers.extend([
                            'follower_count', 'following_count',
                            'mutual_followers_count', 'is_new_to_instagram'
                        ])
                        writer = csv.DictWriter(f, fieldnames=headers)
                        if new_file:
                            writer.writeheader()
                        for row in followers:
                            row.update(follower_metrics[row['pk']])
                            writer.writerow(row)
                else:
                    print(Mapping.aggregate_field_names(followers))
                followers = []
                follower_metrics = {}
                cooldown = 0
            sleep(2)
    except:
        print('Timed out. Sleeping for {0} minutes...'.format(cooldown))
        sleep(60 * cooldown)
        get_insta_followers(cooldown + 60)


def get_tiktok_followers(cooldown=60, max_time='0'):
    try:
        args = {
            'user_id': opts['<user_id>'],
            'count': 100,
            'max_time': max_time,
        }

        # load cursor from save if needed
        if settings['tiktok_cursors'].get(
                'max_time') and opts['--load-cursor']:
            args['max_time'] = settings['tiktok_cursors']['max_time']
            max_time = args['max_time']

        # request from https://rapidapi.com/contact-cmWXEDTql/api/scraptik/
        resp = requests.request('GET',
                                tiktok_api_url,
                                headers={
                                    'X-RapidAPI-Key':
                                    os.getenv('RAPIDAPI_KEY'),
                                    'X-RapidAPI-Host':
                                    'scraptik.p.rapidapi.com'
                                },
                                params=args)
        data = resp.json()
        followers = data['followers']
        has_more = data['has_more']
        min_time = data['min_time']

        print("Scraping from max_time:\t{0}\nmin_time:\t{1}\n".format(
            max_time, min_time))

        # write to file or print
        if not is_inspecting:
            new_file = not os.path.isfile(opts['<output>'])
            with open(opts['<output>'], 'a', encoding='UTF8') as f:
                writer = csv.DictWriter(
                    f, fieldnames=Mapping.aggregate_field_names(followers))
                if new_file:
                    writer.writeheader()
                for row in followers:
                    writer.writerow(row)

            settings['tiktok_cursors']['max_time'] = min_time
            update_settings_file()

            if has_more:
                sleep(5)
                get_tiktok_followers(max_time=min_time)
            else:
                print('Finished TikTok scraping. Stopping...')
        else:
            print(Mapping.aggregate_field_names(data['followers']))
    except Exception as e:
        print('TikTok error:', e)
        print('Timed out. Sleeping for {0} minutes...'.format(cooldown))
        sleep(60 * cooldown)
        get_tiktok_followers(cooldown + 60)


# parse options & run jobs
if __name__ == '__main__':
    opts = docopt(__doc__, version='Social Info 1.0')
    is_inspecting = opts['--inspect']

    if opts['followers']:
        # for instagram
        if opts['instagram']:
            # paginate through <user_id>'s followers
            get_insta_followers()
        # for twitter
        elif opts['twitter']:
            current = 0

            # paginate through <user_id>'s followers
            cursor = None
            if opts['--load-cursor']:
                if settings['twitter_cursors'].get('next_cursor'):
                    cursor = settings['twitter_cursors']['next_cursor']

            for results in tweepy.Paginator(
                    twitter_api.get_users_followers,
                    opts['<user_id>'],
                    user_fields='verified,public_metrics',
                    pagination_token=cursor,
                    limit=100):
                meta = results.meta
                next_cursor = meta['next_token']
                prev_cursor = None
                if meta.get('previous_token'):
                    prev_cursor = meta['previous_token']

                current += 1
                print(
                    "Scraping page:\t{0}\nprev_cursor:\t{1}\nnext_cursor:\t{2}\n"
                    .format(current, prev_cursor, next_cursor))

                settings['twitter_cursors'] = {
                    'next_cursor': next_cursor,
                    'prev_cursor': prev_cursor
                }

                update_settings_file()

                # write to file or print
                if not is_inspecting:
                    new_file = not os.path.isfile(opts['<output>'])
                    with open(opts['<output>'], 'a', encoding='UTF8') as f:
                        writer = csv.DictWriter(f,
                                                fieldnames=[
                                                    'id', 'username',
                                                    'followers_count',
                                                    'following_count',
                                                    'tweet_count',
                                                    'listed_count', 'verified'
                                                ])
                        if new_file:
                            writer.writeheader()
                        for user in results.data:
                            data = user.data
                            metrics = data['public_metrics']
                            writer.writerow({
                                'id':
                                user.data['id'],
                                'username':
                                user.data['username'],
                                'followers_count':
                                metrics['followers_count'],
                                'following_count':
                                metrics['following_count'],
                                'tweet_count':
                                metrics['tweet_count'],
                                'listed_count':
                                metrics['listed_count'],
                                'verified':
                                data['verified']
                            })

                # delay
                sleep(1)

        # for tiktok (in-progress)
        elif opts['tiktok']:
            get_tiktok_followers()
