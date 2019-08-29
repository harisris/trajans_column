import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

import patoolib
from comsear import ComicVineClient
import pprint
import functools
import json
import re
import os
import datetime
import numpy as np
api_key = 'be9301c9c1770a0c729635a06a4513ad9d95410c'
cv = ComicVineClient(api_key)
root = './data/'

Base = declarative_base()

class Volume(Base):
    __tablename__ = 'volume'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    aliases = Column(String)
    api_detail_url = Column(String)
    character_credits = Column(String)
    concept_credits = Column(String)
    count_of_issues = Column(Integer)
    data_added = Column(String)
    data_last_updated = Column(String)
    deck = Column(String)
    description = Column(String)
    first_issue = Column(String)
    image = Column(String)
    last_issue = Column(String)
    location_credits = Column(String)
    object_credits = Column(String)
    person_credits = Column(String)
    publisher = Column(String)
    site_detail_url = Column(String)
    start_year = Column(String)
    team_credits = Column(String)


