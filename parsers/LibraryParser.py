from .VolumeParser import Vanilla as volume_parser
from scanners.vanilla import Vanilla as library_scanner
from pathlib import Path
from tqdm.auto import tqdm

from utils.config import ConfigManager
from comicvine import ComicVineClient

manager = ConfigManager()

class Vanilla:
    def __init__(self, library_path):
        self.library_path = Path(library_path).resolve()
        self.n_comics = None
        self.n_volumes = None
        self.folder_paths = []
        self.library_dict = {}
        self.api_key = manager.read_api_key()

    def library_watchdog(self):
        pass

    def scan_root_folder(self):
        #folders = list({each.parent for each_ext in ['*.cbr', '*.cbz'] for each in self.library_path.rglob(each_ext)})
        scanner = library_scanner(library_path=self.library_path)
        self.library_dict = scanner.scan()

    def volumify(self):
        for each in self.library_dict:
             for each_type in self.library_dict[each]:
                self.library_dict[each][each_type]['parser'] = volume_parser(name=each, volume_type=each_type, path=self.library_dict[each][each_type]['path'], paths_in_folder=self.library_dict[each][each_type]['paths_in_folder'])

    def parse_library(self):
        [self.library_dict[each_volume][each_type]['parser'].parseVolume() for each_volume in self.library_dict.keys() for each_type in self.library_dict[each_volume].keys()]

    def search_volumes(self):
        vine_client = ComicVineClient(manager.read_api_key())
        volume_loop = tqdm(self.library_dict.keys())
        for each_volume in volume_loop:
            for each_type in self.library_dict[each_volume].keys():
                self.library_dict[each_volume][each_type]['parser'].searchQuery(vine_client=vine_client, tqdm_loop=volume_loop)

#        [self.library_dict[each_volume][each_type]['parser'].searchQuery(vine_client=vine_client) for each_volume in self.library_dict.keys() for each_type in self.library_dict[each_volume].keys()]

    def show_best(self):
        volume_loop = tqdm(self.library_dict.keys())
        for each_volume in volume_loop:
            for each_type in self.library_dict[each_volume].keys():
                self.library_dict[each_volume][each_type]['parser'].findBestSearch(api_key=self.api_key, tqdm_loop=volume_loop)

#        [self.library_dict[each_volume][each_type]['parser'].findBestSearch(api_key=self.api_key) for each_volume in self.library_dict.keys() for each_type in self.library_dict[each_volume].keys()]

    def confirm_best(self):
        [self.library_dict[each_volume][each_type]['parser'].confirmResult() for each_volume in self.library_dict.keys() for each_type in self.library_dict[each_volume].keys()]


