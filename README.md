# Trajans_Column
(Name still in working, but apparently the first visual narratives were found in [Trajan's Column](https://en.wikipedia.org/wiki/History_of_comics))


Another simple Python based management tool to organise comics, retrieve metadata from Comicvine, and host it as a Flask server. The whole tool is focussed on being modular where one can use their own custom directory scanners, file name parsers, and database access tool. So in theory it can be extended for any kind of data. A vanilla version is also provided using regex expressions. Flask-SQLAlchemy is being used for ORM, and Flask itself will provide the REST APIs.

Still at it's infancy, and has a long way to go to come close to the likes of Calibre and Plex.

Project roadmap :
- [ ] A properly functioning Flask server to begin with (Duh.)
- [ ] Security aspects. (A bit of noob here, but we'll see.)
- [ ] GUI. (For both server side, and client side. The server side involves library generation, matching UI, a neat way to show, story arcs.) For the first phase, the GUI is going to be built for MacOS environment, and a support reading app for iOS, because they are pretty.

Credits to jessebraham/comicvine-search for the comicvine search code. 


