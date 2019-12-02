from .ComicParser import Vanilla as comic_parser


import requests
from urllib.request import urlretrieve
import numpy as np

class Vanilla:
    def __init__(self, name=None, volume_type=None, path=None, paths_in_folder=None):
        self.volume_name = name
        self.volume_path = path
        self.volume_type = volume_type
        self.volumeDict = {'paths_in_folder' : paths_in_folder, 'assets_in_folder': {}}
        self.asset_count = 0
        self.comic_years = None
        self.volume_initiated = False
        self.update_index = 0
        self.volumeTable = None
        self.searchReturned = None

    def scan_volume(self): #Adds path and volume name to the parser object.
        """
        Need to make sure, only if the parser is not initiated by a library, we need to add pathlib actions here. We can use None passes.
        """
        pass

    def parseVolume(self): # Also parses comic. 
        if '(' in self.volume_name:
            self.volume_name = self.volume_name.split(' (')[0].strip()
        else:
            self.volume_name = self.volume_name
        #print(self.volume_name)
        self.volumeDict['from_file_volume_name'] = self.volume_name
        for each_asset in self.volumeDict['paths_in_folder']:
            comic = comic_parser(each_asset) #convert to path join volume path and entry
            comic.parseComic()
            self.volumeDict['assets_in_folder'].update({comic.comic_name : comic})
#         print(str(len(self.volumeDict['comics_in_folder']))+' comics added in volume ' + self.volume_name +'.')    
        self.asset_count = len(self.volumeDict['assets_in_folder'])
        self.comic_years = {self.volumeDict['assets_in_folder'][key].comic_year for key in self.volumeDict['assets_in_folder'].keys() if self.volumeDict['assets_in_folder'][key].comic_year}
        del(self.volumeDict['paths_in_folder'])

    def searchQuery(self, vine_client, tqdm_loop=None): #Search ComicVine Server for metadata
        years = [self.volumeDict['assets_in_folder'][key].comic_year for key in self.volumeDict['assets_in_folder'].keys() if self.volumeDict['assets_in_folder'][key].comic_year]
        searchtext = self.volumeDict['from_file_volume_name']
        if self.comic_years:
            searchtext += (' '+str(min(self.comic_years)))
        if tqdm_loop:
            tqdm_loop.set_postfix_str(s='Querying for '+searchtext)
        firstresponse = vine_client.search(searchtext, resources=['volume']) #Search for volume name with year
        self.searchReturned = firstresponse.results

    def findBestSearch(self, api_key, deep_check=True, tqdm_loop = None):
        from fuzzywuzzy import fuzz
        HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:7.0) '
                     'Gecko/20130825 Firefox/36.0'}
        params = {'api_key':api_key, 'format': 'json'}
        """
        Finding best search among Volumes. 2 main information considered
        here are number of assets in folder folder (which is assumed to be
        total number of issues in that volume) and year range obtained
        from comic file names.

        First Result | No. of Issues | Year | Score | Result
              o               o          o      80      o
              o               X          o      70      o
              X               o          o      50      o
              o               o          X      40      X -
              X               X          o      40      X |
              o               X          X      30      X |-- Fuzzy search for these guys
              X               o          X      10      X -
        """
        if tqdm_loop:
            tqdm_loop.set_postfix_str(s='Finding best match for '+self.volume_name)
#        print("Finding best match")
        existing_comics = list(self.volumeDict['assets_in_folder'].keys())
        best_index = 0
        for indx, each_result in enumerate(self.searchReturned):
            if indx is 0:
                each_result['match_score'] = 30.0 #First result returned is the best result.
            elif indx is not 0:
                each_result['match_score'] = 0.0
            if self.asset_count == each_result['count_of_issues']:
                each_result['match_score'] += 10.0
            if self.comic_years:
                if (min(self.comic_years)<=int(each_result['start_year'])<=max(self.comic_years)):
                    each_result['match_score'] +=40.0
            if each_result['match_score']>=np.array(self.searchReturned)[best_index]['match_score']: #Also assumed that search results are coming back sorted in relavance.
                best_index = indx
        self.volumeDict['best_search']=np.array(self.searchReturned)[best_index]
        if deep_check and self.volumeDict['best_search']['match_score']<=40: #Deep fuzzy search over titles in volume and existing comics.
            if tqdm_loop:
                tqdm_loop.set_postfix_str(s='Best score is only '+ str(each_result['match_score'])+'. Performing deep search for '+self.volume_name+'.')
            for indx, each_result in enumerate(self.searchReturned):
                detailresponse = requests.get(each_result['api_detail_url'], headers=HEADERS, params=params)
                titles_in_vol = [each['name'] for each in detailresponse.json()['results']['issues']]
                each_result['match_score'] +=fuzz.token_set_ratio(titles_in_vol, existing_comics) #Levenshtein Distance
                if each_result['match_score']>=np.array(self.searchReturned)[best_index]['match_score']: #Also assumed that search results are coming back sorted in relavance.
                    best_index = indx

        self.volumeDict['best_search']=np.array(self.searchReturned)[best_index]
        #print('Match Score : '+ str(self.volumeDict['best_search']['match_score']))

    def confirmResult(self):
        from IPython.display import clear_output
        from utils.utils import print_com_meta, query_yes_no, sanitised_input
        clear_output()
        print('Volume Name from File System : '+self.volume_name)
        print('\nType : '+self.volume_type)
        print('\nNo. of issues within folder : '+str(self.asset_count))
        print('\nRange of years within folder : '+str(self.comic_years))

        print_com_meta(self.volumeDict['best_search'], 'Best Result:')
        confirmation = query_yes_no("Is the information correct?")
        choice = None
        while True:
            clear_output()
            print('\nNo. of issues within folder : '+str(self.asset_count))
            print('Range of years within folder : '+str(self.comic_years))
            if not confirmation: 
                for idx, each in enumerate(self.searchReturned):
                    print_com_meta(each, idx+1)
                choice = sanitised_input("Please make a manual choice between 1-10 : ", int, 1,10)
                print_com_meta(self.searchReturned[choice-1], 'Your Choice : ')
                confirmation = query_yes_no("Is the information correct?")
            else:
                if choice:
                    self.volumeDict['best_search'] = self.searchReturned[choice-1]
                break

    def fetchVolumeMetadata(self, api_key):
        HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:7.0) '
                     'Gecko/20130825 Firefox/36.0'}
        params = {'api_key':api_key, 'format': 'json'}

        detailresponse = requests.get(self.volumeDict['best_search']['api_detail_url'], headers=HEADERS, params=params)
        fetched_volume = detailresponse.json()
        self.volumeDict['detailed_meta'] = fetched_volume['results']
        #Image Directory
        orig_directory = './resources/Images/VolumeArt/'
        img_name = os.path.basename(self.volumeDict['detailed_meta']['image']['original_url'])
        img_path = os.path.join(orig_directory,img_name)
        #Fetch Image
        urlretrieve(self.volumeDict['detailed_meta']['image']['original_url'], img_path)
        self.volume_initiated = True
        volume = Volume(
                        id = self.volumeDict['detailed_met']['id'],
                        name = self.volumeDict['detailed_meta']['name'],
                        aliases = self.volumeDict['detailed_meta']['aliases'],
                        count_of_issues = self.volumeDict['detailed_meta']['count_of_issues'],
                        date_added = self.volumeDict['detailed_meta']['date_added'],
                        date_last_updated = self.volumeDict['detailed_meta']['date_last_updated'],
                        deck = self.volumeDict['detailed_meta']['deck'],
                        description = re.sub(r'<[^>]*>', '', self.volumeDict['detailed_meta']['description']), #remove all within angle brackets
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
        HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:7.0) '
                     'Gecko/20130825 Firefox/36.0'}
        params = {'api_key':api_key, 'format': 'json'}

        comic_fetch_loop = tqdm(self.volumeDict['detailed_meta']['issues'])
        comicObjects = []
        issue_directory = './resources/Images/IssueArt/'
        for each_issue in comic_fetch_loop:
            per_issue_response = requests.get(each_issue['api_detail_url'], headers=HEADERS, params=params).json()['results']
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
            comic_fetch_loop.set_postfix(Status='Added '+str(comic.name))
        self.volumeTable.comics=set(comicObjects)

    def fetch_arc_data(self):
        pass
        arc_objects = []
        for each_comic in self.volumeTable.comics:
            for each_arc in each_comic['story_arc_credits']:
                arc = Story_Arc()

    def commit_to_db(self, dbpath='sqlite:///comicdb.db'):
        app.config['SQLALCHEMY_DATABASE_URI'] = dbpath
        #db = SQLAlchemy(app)
        #engine = create_engine(dbpath, echo=False)
        #Base.metadata.create_all(engine)
        #Session = sessionmaker(bind=engine)
        #session = Session()
        db.session.add(self.volumeTable)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        db.session.close()
        engine.dispose()

