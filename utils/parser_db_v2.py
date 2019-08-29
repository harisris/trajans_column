import requests
from dbobjects import *
from urllib.request import urlretrieve
from comsear import ComicVineClient
import re
import os
from tqdm.auto import tqdm
root = './data/'

class ComicParser():
    def __init__(self, path):
        self.comic_name = None
        self.comic_year = None
        self.issue_number = None
        self.comic_path = path
        self.comic_metadata = {}
        self.comic_initiated = False

    def parseComic(self):
        self.comic_name = os.path.splitext(os.path.basename(self.comic_path))[0]
        year_within_brackets = re.findall(r'\(([12]\d{3})', self.comic_name)[0]
        if (len(year_within_brackets) == 4): #Stupid way of doing but good for now.
            self.comic_year = int(year_within_brackets)
        else:
            self.comic_year = 0
        self.issue_number = re.findall(r"(\d+\.?\d?[a-zA-Z]{0,3}?)(?:\s*\(of|\s*\([12]\d{3}\))", self.comic_path)
        #Get the digits or digits with point number (19.1) or digits followed by letters (19.INH) either before "(of" or before a year. 

class VolumeParser:
    def __init__(self, path):
        self.volume_name = None
        self.type = None #TPB or Single Issues
        self.volume_path = path
        self.volume_initiated = False
        self.volumeDict = {'comics_in_folder' : {} } 
        self.volumeFetch = True
        self.volumeTable = None
        self.HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:7.0) '
                     'Gecko/20130825 Firefox/36.0'}
        self.params = {'api_key':api_key, 'format': 'json'}

    def parseVolume(self):
        if 'Issues' in os.listdir(self.volume_path):
            comic_dir = os.path.join(self.volume_path, 'Issues')
        else:
            comic_dir = self.volume_path
        if '(' in self.volume_path:
            self.volume_name = os.path.basename(self.volume_path).split(' (')[0]
        else:
            self.volume_name = os.path.basename(self.volume_path)
        self.volumeDict['from_file_volume_name'] = self.volume_name
        for entry in os.listdir(comic_dir):
            comic = ComicParser(os.path.join(comic_dir,entry)) #convert to path join volume path and entry
            comic.parseComic()
            self.volumeDict['comics_in_folder'].update({comic.comic_name : comic})
        print(str(len(self.volumeDict['comics_in_folder']))+' comics added in volume ' + self.volume_name +'.')

    def findBestSearch(self,api_key):
        """
        Finding best search among Volumes.
        2 main information considered
        here are number of files in folder folder (which is assumed to be
        total number of issues in that volume) and year range obtained
        from comic file names.
        """
        print("Fetching from Comic Vine servers")
        years = [self.volumeDict['comics_in_folder'][key].comic_year for key in self.volumeDict['comics_in_folder'].keys()]
        firstresponse = cv.search((self.volumeDict['from_file_volume_name'] +' '+str(years[0])), resources=['volume']) #Search for volume name with year
        returned = firstresponse.results
        print("Finding best match")
        expected_num_comics = len(self.volumeDict['comics_in_folder'])

        best_index = 0
        for indx, each_result in enumerate(returned):
            if indx is 0:
                each_result['match_score'] = 40.0 #First result returned is the best result.
            elif indx is not 0:
                each_result['match_score'] = 0.0
            if expected_num_comics == each_result['count_of_issues']:
                each_result['match_score'] += 10.0
            if (min(years)<=int(each_result['start_year'])<=max(years)):
                each_result['match_score'] +=40.0
            if each_result['match_score']>np.array(returned)[best_index]['match_score']: #Also assumed that search results are coming back sorted in relavance.
                best_index = indx
        self.volumeDict['best_search']=np.array(returned)[best_index]
        print('Match Score : '+ str(self.volumeDict['best_search']['match_score']))

    def fetchVolumeMetadata(self):
        detailresponse = requests.get(self.volumeDict['best_search']['api_detail_url'], headers=self.HEADERS, params=self.params)
        fetched_volume = detailresponse.json()
        self.volumeDict['detailed_meta'] = fetched_volume['results']
        #Image Directory
        orig_directory = './Resources/Images/VolumeArt/'
        img_name = os.path.basename(self.volumeDict['detailed_meta']['image']['original_url'])
        img_path = os.path.join(orig_directory,img_name)
        #Fetch Image
        urlretrieve(self.volumeDict['detailed_meta']['image']['original_url'], img_path)
        self.volume_initiated = True

        volume = Volume(
                        id = self.volumeDict['detailed_meta']['id'],
                        name = self.volumeDict['detailed_meta']['name'],
                        aliases = self.volumeDict['detailed_meta']['aliases'],
                        count_of_issues = self.volumeDict['detailed_meta']['count_of_issues'],
                        date_added = self.volumeDict['detailed_meta']['date_added'],
                        date_last_updated = self.volumeDict['detailed_meta']['date_last_updated'],
                        deck = self.volumeDict['detailed_meta']['deck'],
                        description = re.sub(r'<[^>]*>', '', vol1.volumeDict['detailed_meta']['description']), #remove all within angle brackets
                        publisher = self.volumeDict['detailed_meta']['publisher']['name'], #Later to be changed to publisher object
                        start_year = self.volumeDict['detailed_meta']['start_year'],
                        comicvine_api_detail_url = self.volumeDict['detailed_meta']['api_detail_url'],
                        comicvine_image = self.volumeDict['detailed_meta']['image']['original_url'], #image
                        comicvine_site_detail_url = self.volumeDict['detailed_meta']['site_detail_url'],
                        local_path = self.volume_path,
                        local_image_path = img_path,
                        #character_credits = Column(String)
                        #concept_credits = Column(String)
                        #team_credits = Column(String)
                        #location_credits = Column(String)
                        #object_credits = Column(String)
                        #person_credits = Column(String)
                        )
        self.volumeTable = volume

    def fetchComicsMetadata(self, api_key):
        comic_fetch_loop = tqdm(self.volumeDict['detailed_meta']['issues'])
        comicObjects = []
        issue_directory = './Resources/Images/IssueArt/'
        for each_issue in comic_fetch_loop:
            per_issue_response = requests.get(each_issue['api_detail_url'], headers=self.HEADERS, params=self.params).json()['results']
            img_name = os.path.basename(per_issue_response['image']['original_url'])
            img_path = os.path.join(issue_directory,img_name)
            #Fetch Image if doesnt exist
            if not os.path.isfile(img_path):
                urlretrieve(per_issue_response['image']['original_url'], img_path)
            comic = Comic(id = per_issue_response['id'],
                          name = per_issue_response['name'],
                          aliases = per_issue_response['aliases'],
                          deck = per_issue_response['deck'],
                          description = re.sub(r'<[^>]*>', '', per_issue_response['description']),
                          cover_date = per_issue_response['cover_date'],
                          date_added = per_issue_response['date_added'],
                          date_last_updated = per_issue_response['date_last_updated'],
                          issue_number = per_issue_response['issue_number'],
                          comicvine_api_detail_url = per_issue_response['api_detail_url'],
                          comicvine_image = per_issue_response['image']['original_url'],
                          local_image_path = img_path
            )
            comicObjects.append(comic)
            comic_fetch_loop.set_postfix(Status='Added '+str(comic.name)
        self.volumeTable.comics=set(comicObjects)
#             for key in self.volumeDict['comics_in_folder'].keys():
#                 if self.volumeDict['comics_in_folder'][key].issue_number == per_issue_response['issue_number'] and self.volumeDict['comics_in_folder'][key].comic_initiated == False:
#                     self.volumeDict['comics_in_folder'][key].comic_metadata = per_issue_response
#                     self.volumeDict['comics_in_folder'][key].comic_initiated = True
