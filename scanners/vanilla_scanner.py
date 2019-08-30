import pathlib

def scan(library_path, extensions = ['*.cbr', '*.cbz'], collection_types = ['Issues', 'TPB']):
    folddict = {}
    directory_dict = {}
    for each_ext in extensions:
        for each in library_path.rglob(each_ext):
            if each.parent.resolve() in folddict:
                folddict[each.parent.resolve()].append(each.resolve())
            else:
                folddict[each.parent.resolve()] = [each.resolve()]
    for each in folddict:
        if any(collection in each.name for collection in collection_types):
            for collection in collection_types:
                if collection in each.name:
                    if each.parent.name not in directory_dict:
                        directory_dict[each.parent.name] = {collection.lower() : {'path' : [each], 'assets_in_folder' : folddict[each]}}
                    else:
                        if collection.lower() not in directory_dict[each.parent.name]:
                            directory_dict[each.parent.name].update({collection.lower() : {'path' : [each], 'assets_in_folder' : folddict[each]}})
                        else:
                            #Check here for diffs (Next version update)
                            directory_dict[each.parent.name][collection.lower()]['path'].append(each)
        else:
            directory_dict[each.name] = {'issues' : {'path' : each, 'assets_in_folder' : folddict[each]}}
    return(directory_dict)
