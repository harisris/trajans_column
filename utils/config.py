import configparser
import argparse
from pathlib import Path

class ConfigManager():
    def  __init__(self):
        self.comicvine_config_file = Path(Path.home()/'.comicvine.ini')
        self.config = configparser.ConfigParser()

    def update_api_key(self, api_key, email_id):
        if not self.comicvine_config_file.is_file():
            self.config['ComicVine'] = {'api_key':api_key,
                                   'email_id':email_id}
            with open (self.comicvine_config_file, 'w') as configfile:
                self.config.write(configfile)
        else:
            self.config.read(self.comicvine_config_file)
            print('Config File already exists.')
            if self.config['ComicVine']['api_key'] != api_key:
                print('Old Key : '+self.config['ComicVine']['api_key'])
                config['ComicVine']['api_key'] = api_key
                with open (self.comicvine_config_file, 'w') as configfile:
                    self.config.write(configfile)
                print('New Key : '+self.config['ComicVine']['api_key'])
            else:
                print('Nothing to change here. Key already exists')

    def read_api_key(self):
        if not self.comicvine_config_file.is_file():
            print("Config File doesn't exist. Create one.")
        else:
            self.config.read(self.comicvine_config_file)
            return self.config['ComicVine']['api_key']

def main(api_key, email_id):
    manager = ConfigManager()
    manager.update_api_key(api_key=api_key, email_id=email_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Wrapper Function to add Comic Vine API Key. (You can generate it from the website.)')
    parser.add_argument('email_id', help='Email ID used for registering in Comicvine.', required=True)
    parser.add_argument('api_key', help='ComicVine API Key', required=True)
    args = parser.parse_args()
    main(args.api_key, args.email_id)

