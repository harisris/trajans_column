from app import db
volume_comics = db.Table('volumecomics',
			db.Column('comic_id', db.Integer, db.ForeignKey('comic.id'), primary_key=True),
                        db.Column('volume_id', db.Integer, db.ForeignKey('volume.id'), primary_key=True))


class Comic(db.Model):
#    __tablename__ = 'comic'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    aliases = db.Column(db.String)
    deck = db.Column(db.String)
    description = db.Column(db.String)
    concept_credits = db.Column(db.String)
    character_credits = db.Column(db.String)
    location_credits = db.Column(db.String)
    story_arc_credits = db.Column(db.String)
    team_credits = db.Column(db.String)
    person_credits = db.Column(db.String)
    object_credits = db.Column(db.String)
    character_died_in = db.Column(db.String)
    cover_date = db.Column(db.String)
    date_added = db.Column(db.String)
    date_last_updated = db.Column(db.String)
    issue_number = db.Column(db.String)
    comicvine_api_detail_url = db.Column(db.String)
    comicvine_image = db.Column(db.String) #image
    comicvine_site_detail_url = db.Column(db.String)
    local_path = db.Column(db.String)
    local_image_path = db.Column(db.String)

class Volume(db.Model):
#    __tablename__ = 'volume'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    aliases = db.Column(db.String)
    character_credits = db.Column(db.String)
    concept_credits = db.Column(db.String)
    count_of_issues = db.Column(db.Integer)
    date_added = db.Column(db.String)
    date_last_updated = db.Column(db.String)
    deck = db.Column(db.String)
    description = db.Column(db.String)

    location_credits = db.Column(db.String)
    object_credits = db.Column(db.String)
    person_credits = db.Column(db.String)
    publisher = db.Column(db.String)

    start_year = db.Column(db.String)
    team_credits = db.Column(db.String)
    comicvine_api_detail_url = db.Column(db.String)
    comicvine_image = db.Column(db.String) #image
    comicvine_site_detail_url = db.Column(db.String)
    local_path = db.Column(db.String)
    local_image_path = db.Column(db.String)
    comics = db.relationship("Comic",
                    secondary=volume_comics,
                    lazy='subquery',
                    backref=db.backref("volumes"),
                    collection_class=set)
