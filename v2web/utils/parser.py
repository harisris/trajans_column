import patoolib
from comsear import ComicVineClient
import pprint
import functools
import requests
import json
import re
import os
import datetime
import numpy as np
api_key = 'be9301c9c1770a0c729635a06a4513ad9d95410c'
cv = ComicVineClient(api_key)
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
        self.HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:7.0) '
                     'Gecko/20130825 Firefox/36.0'}
        self.params = {'api_key':api_key, 'format': 'json'} 
        
    def parseVolume(self):
        self.volume_name=os.path.basename(self.volume_path).split(' (')[0] 
        self.volumeDict['from_file_volume_name'] = self.volume_name        
        for entry in os.listdir(self.volume_path):
            comic = ComicParser(os.path.join(self.volume_path,entry)) #convert to path join volume path and entry
            comic.parseComic()            
            self.volumeDict['comics_in_folder'].update({comic.comic_name : comic})
                                
        print(str(len(self.volumeDict['comics_in_folder']))+' comics added in volume ' + self.volume_name +'.')    
        
    def fetchVolumeMetadata(self, api_key):                
        """        
        Finding best search among Volumes. 2 main information considered 
        here are number of files in folder folder (which is assumed to be 
        total number of issues in that volume) and year range obtained 
        from comic file names.        
        
        """
        print("Fetching from Comic Vine servers")
        firstresponse = cv.search(self.volumeDict['from_file_volume_name'], resources=['volume'])
        returned = firstresponse.results
        print("Finding best match")
        expected_num_comics = len(self.volumeDict['comics_in_folder'])    
        years = [self.volumeDict['comics_in_folder'][key].comic_year for key in self.volumeDict['comics_in_folder'].keys()]
        best_index = 0
        for indx, each_result in enumerate(returned):    
            each_result['match_score'] = 0.0
            if expected_num_comics == each_result['count_of_issues']:
                each_result['match_score'] += 20.0        
            if (min(years)<=int(each_result['start_year'])<=max(years)):
                each_result['match_score'] +=20.0
            if each_result['match_score']>np.array(returned)[best_index]['match_score']: #Also assumed that search results are coming back sorted in relavance.
                best_index = indx
        self.volumeDict['best_search']=np.array(returned)[best_index]
        
        detailresponse = requests.get(self.volumeDict['best_search']['api_detail_url'], headers=self.HEADERS, params=self.params)
        fetched_volume = detailresponse.json()
        self.volumeDict['detailed_meta'] = fetched_volume['results']
        self.volume_initiated = True
        print('Match Score : '+ str(self.volumeDict['best_search']['match_score']))
        
    def fetchComicsMetadata(self, api_key):
        for each_issue in self.volumeDict['detailed_meta']['issues']:
            per_issue_response = requests.get(each_issue['api_detail_url'], headers=self.HEADERS, params=self.params).json()['results']            
            for key in self.volumeDict['comics_in_folder'].keys():
                if self.volumeDict['comics_in_folder'][key].issue_number == per_issue_response['issue_number'] and self.volumeDict['comics_in_folder'][key].comic_initiated == False:
                    self.volumeDict['comics_in_folder'][key].comic_metadata = per_issue_response
                    self.volumeDict['comics_in_folder'][key].comic_initiated = True
            