from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

Base = declarative_base()

association_table = Table('comic_volume_association', Base.metadata,
    Column('comic_id', Integer, ForeignKey('comic.id')),
    Column('volume_id', Integer, ForeignKey('volume.id'))
)


class Comic(Base):
    __tablename__ = 'comic'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    aliases = Column(String)
    deck = Column(String)
    description = Column(String)
    concept_credits = Column(String)
    character_credits = Column(String)
    location_credits = Column(String)
    story_arc_credits = Column(String)
    team_credits = Column(String)
    person_credits = Column(String)
    object_credits = Column(String)
    character_died_in = Column(String)
    cover_date = Column(String)
    date_added = Column(String)
    date_last_updated = Column(String)
    issue_number = Column(String)
    comicvine_api_detail_url = Column(String)
    comicvine_image = Column(String) #image
    comicvine_site_detail_url = Column(String)
    local_path = Column(String)
    local_image_path = Column(String)

class Volume(Base):
    __tablename__ = 'volume'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    aliases = Column(String)
    character_credits = Column(String)
    concept_credits = Column(String)
    count_of_issues = Column(Integer)
    date_added = Column(String)
    date_last_updated = Column(String)
    deck = Column(String)
    description = Column(String)

    location_credits = Column(String)
    object_credits = Column(String)
    person_credits = Column(String)
    publisher = Column(String)

    start_year = Column(String)
    team_credits = Column(String)
    comicvine_api_detail_url = Column(String)
    comicvine_image = Column(String) #image
    comicvine_site_detail_url = Column(String)
    local_path = Column(String)
    local_image_path = Column(String)
    comics = relationship("Comic",
                    secondary=association_table,
                    backref="volumes",
                    collection_class=set)

