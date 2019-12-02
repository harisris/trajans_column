import pathlib


class Vanilla:
    def __init__(self, library_path, extensions = ['*.cbr', '*.cbz'], collection_types = ['Issues', 'TPB', 'Annuals', 'Omnibus']):
        self.library_path = library_path
        self.extensions = extensions
        self.collection_types = collection_types
        self.directory_dict = {}

    def scan(self):
        folddict = {}
        for each_ext in self.extensions:
            for each in self.library_path.rglob(each_ext):
                if each.parent.resolve() in folddict:
                    folddict[each.parent.resolve()].append(each.resolve())
                else:
                    folddict[each.parent.resolve()] = [each.resolve()]
        for each in folddict:
            if any(collection in each.name for collection in self.collection_types):
                for collection in self.collection_types:
                    if collection in each.name:
                        if each.parent.name not in self.directory_dict:
                            self.directory_dict[each.parent.name] = {collection.lower() : {'path' : [each], 'paths_in_folder' : folddict[each]}}
                        else:
                            if collection.lower() not in self.directory_dict[each.parent.name]:
                                self.directory_dict[each.parent.name].update({collection.lower() : {'path' : [each], 'paths_in_folder' : folddict[each]}})
                            else:
                                #Check here for diffs (Next version update)
                                self.directory_dict[each.parent.name][collection.lower()]['path'].append(each)
            else:
                self.directory_dict[each.name] = {'issues' : {'path' : each, 'paths_in_folder' : folddict[each]}}
        return(self.directory_dict)
