import configparser
import argparse
from pathlib import Path

comicvine_config_file = Path(Path.home()/'.comicvine.ini')

def update_api_key(api_key, email_id='hari.sri.s@gmail.com'):
    config = configparser.ConfigParser()
    if not comicvine_config_file.is_file():
        config['ComicVine'] = {'api_key':api_key,
                               'email_id':email_id}
        with open (comicvine_config_file, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(comicvine_config_file)
        print('Config File already exists.')
        if config['ComicVine']['api_key'] != api_key:
            print('Old Key : '+config['ComicVine']['api_key'])
            config['ComicVine']['api_key'] = api_key
            with open (comicvine_config_file, 'w') as configfile:
                config.write(configfile)
            print('New Key : '+config['ComicVine']['api_key'])
        else:
            print('Nothing to change here. Key already exists')

def main(api_key):
    update_api_key(api_key=api_key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Wrapper Function to add Comic Vine API Key. (You can generate it from the website.)')
    parser.add_argument('api_key', help='ComicVine API Key', required=True)
    args = parser.parse_args()
    main(args.api_key)

def read_api_key():
    config = configparser.ConfigParser()
    if not comicvine_config_file.is_file():
        print("Config File doesn't exist. Create one.")
    else:
        config.read(comicvine_config_file)
        return config['ComicVine']['api_key']
