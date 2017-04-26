from app import db
from sqlalchemy.dialects.postgresql import JSON
#export DATABASE_URL="postgresql://localhost/youtubed"

class Results(db.Model):
	__tablename__ = 'searchresult'

	id = db.Column(db.Integer, primary_key=True)
	vid_idd = db.Column(db.String())
	vid_namee = db.Column(db.String())
	vid_img = db.Column(db.String())



	def __init__(self, vid_id, vid_name, vid_img):
		self.vid_idd = vid_id
		self.vid_namee = vid_name
		self.vid_img = vid_img



	def __repr__(self):
		return '<id {}>'.format(self.id)