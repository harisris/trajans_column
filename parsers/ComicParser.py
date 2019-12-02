import re
class Vanilla(): #Parser object to extract name, first year and issue number.
    def __init__(self, path):
        self.comic_name = None
        self.comic_year = None
        self.issue_number = None
        self.comic_path = path
        self.comic_metadata = {}
        self.comic_initiated = False

    def parseComic(self):
        self.comic_name = self.comic_path.name #os.path.splitext(os.path.basename(self.comic_path))[0]
        years = re.findall(r'\(([12]\d{3})', self.comic_name)
        if years:
            year_within_brackets = years[0]
            if (len(year_within_brackets) == 4): #Stupid way of doing but good for now.
                self.comic_year = int(year_within_brackets)
            else:
                self.comic_year = 0
        self.issue_number = re.findall(r"(\d+\.?\d?[a-zA-Z]{0,3}?)(?:\s*\(of|\s*\([12]\d{3}\))", self.comic_name) #Get the digits or digits with point number (19.1) or digits followed by letters (19.INH) either before "(of" or before a year. 
