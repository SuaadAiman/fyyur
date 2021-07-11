#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import traceback
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate=Migrate(app,db)

# Done: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    address = db.Column(db.String)
    website_link = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    genres=db.Column(db.String)
    #upcoming_shows=db.Column()
    #num_upcoming_shows = db.Column(db.Integer)
    #past_shows=db.Column()
    #past_shows_count=db.Column(db.Integer)
    shows=db.relationship('show', backref='venue' ,
    cascade="all, delete-orphan",
    lazy='dynamic')

    # Done: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website=db.Column(db.String)
    seeking_venue=db.Column(db.Boolean)
    seeking_description=db.Column(db.String)
    shows=db.relationship('show', backref='artist', cascade="all, delete-orphan",
    lazy='dynamic')
    
    # Done: implement any missing fields, as a database migration using Flask-Migrate
class show(db.Model):
    __tablename__ = 'show'
    id=db.Column( db.Integer, primary_key=True)
    venue_id=db.Column( db.Integer, db.ForeignKey('Venue.id'),)
    artist_id=db.Column( db.Integer, db.ForeignKey('Artist.id'),)
    start_time=db.Column(db.Date)
# Done Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")#https://www.programiz.com/python-programming/datetime/current-datetime
  venues_in_database=Venue.query.order_by(Venue.city,Venue.id).all()
  print(venues_in_database)
  state_city=[]
  data=[]
  for v in venues_in_database:
        upcoming_shows= v.shows.filter(show.start_time > now).all()
        if state_city == v.city :
            data[len(data) - 1]["venues"].append({
              "id": v.id,
              "name": v.name,
              "num_upcoming_shows": len(upcoming_shows)
            })
        else:
            print(v.city )
            state_city = v.city 
            data.append({
              "city": v.city,
              "state": v.state,
              "venues": [{
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": len(upcoming_shows)
              }]
            })
            print(data)

  """ data.append([{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }])"""
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  venues=Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()#https://stackoverflow.com/questions/4926757/sqlalchemy-query-where-a-column-contains-a-substring
  response=[]
  now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  response = {
    "count": len(venues),
    "data": []
  }
  for v in venues:
    print(v.shows.filter(show.start_time > now).all().count)
    upcoming_shows = v.shows.filter(show.start_time > now).all()
    response["data"].append({
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": len(upcoming_shows),
    })
  print(response)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # Done: replace with real venue data from the venues table, using venue_id
  v=Venue.query.get(venue_id)
  showss=v.shows

  data={
    "id": v.id,
    "name": v.name,
    "genres": v.genres,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website_link,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  #now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")'
  #now = datetime.date(datetime.now.year,datetime.now.month,datetime.now.day)
  now = datetime.today().date()
  past_shows_count=0
  upcoming_shows_count=0
  for s in showss:
    print(now)
    print(s.start_time)
    #format_datetime(s.start_time, format='medium')
    if s.start_time<now:
      print("")
      #[len(data1) - 1]
      data["past_shows"].append({
              "artist_id": s.artist_id,
              "artist_name": s.artist.name,
              "artist_image_link": s.artist.image_link,
              "start_time": str(s.start_time)
            })
      past_shows_count=past_shows_count+1
      
    else:
      #[len(data1) - 1]
      data["upcoming_shows"].append({
              "artist_id": s.artist_id,
              "artist_name": s.artist.name,
              "artist_image_link": s.artist.image_link,
              "start_time": str(s.start_time)
            })
      upcoming_shows_count=upcoming_shows_count+1
      
  data["past_shows_count"]=past_shows_count
  data["upcoming_shows_count"]=upcoming_shows_count

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state= request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  website_link = request.form.get('website_link')
  seeking_talent = request.form.get('seeking_talent')
  seeking_description = request.form.get('seeking_description')
  print(name,city,state,address,phone)
  try:
    venue=Venue(name=name,city=city,state=state,address=address,phone=phone,image_link=image_link,genres=genres,
    facebook_link=facebook_link,website_link=website_link,seeking_talent=seeking_talent,seeking_description=seeking_description)
  # Done: insert form data as a new Venue record in the db, instead
    db.session.add(venue)
    # Done: modify data to be the data object returned from db insertion
     # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    db.session.commit()
  except Exception as e:
   db.session.rollback()
   print(sys.exc_info())
   print(traceback.format_exc())
   print(e)
   flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
   # Done: on unsuccessful db insert, flash an error instead.
  finally:
   db.session.close()
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    #v = Venue.query.get(venue_id) 
    Venue.query.filter_by(id=venue_id).delete()
    #db.session.delete(v)
    db.session.commit()
    print("kkkkkkkkkkkkkk")
    flash('Venue ' + request.form['name'] + ' was successfully deleted!')
  except Exception as e:
   db.session.rollback()
   print("ttttttttttttttttttttt")
   flash('An error occurred. Venue ' + request.form['name'] + ' could not be deleted.')
  finally:
   db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Done: replace with real data returned from querying the database
  artists_in_database=Artist.query.all()
  print(artists_in_database)
  data=[]
  for a in artists_in_database:
    data.append({
      "id": a.id,
      "name": a.name,
    })
    print(data)
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artists=Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()#https://stackoverflow.com/questions/4926757/sqlalchemy-query-where-a-column-contains-a-substring
  response=[]
  now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  response = {
    "count": len(artists),
    "data": []
  }
  for a in artists:
    upcoming_shows = a.shows.filter(show.start_time > now).all()
    response["data"].append({
        "id": a.id,
        "name": a.name,
        "num_upcoming_shows": len(upcoming_shows),
    })
  print(response)
  """  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }"""
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # Done: replace with real artist data from the artist table, using artist_id
  a=Artist.query.get(artist_id)
  showss=a.shows

  data={
    "id": a.id,
    "name": a.name,
    "genres": a.genres,
    "city": a.city,
    "state": a.state,
    "phone": a.phone,
    "website": a.website,
    "facebook_link": a.facebook_link,
    "seeking_venue": a.seeking_venue,
    "seeking_description": a.seeking_description,
    "image_link": a.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  #now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")'
  #now = datetime.date(datetime.now.year,datetime.now.month,datetime.now.day)
  now = datetime.today().date()
  past_shows_count=0
  upcoming_shows_count=0
  for s in showss:
    print(now)
    print(s.start_time)
    #format_datetime(s.start_time, format='medium')
    if s.start_time<now:
      print("")
      #[len(data1) - 1]
      data["past_shows"].append({
              "venue_id": s.venue_id,
              "venue_name": s.venue.name,
              "venue_image_link": s.venue.image_link,
              "start_time": str(s.start_time)
            })
      
      past_shows_count=past_shows_count+1
      
    else:
      #[len(data1) - 1]
      data["upcoming_shows"].append({
              "venue_id": s.venue_id,
              "venue_name": s.venue.name,
              "venue_image_link": s.venue.image_link,
              "start_time": str(s.start_time)
            })
      upcoming_shows_count=upcoming_shows_count+1
      
  data["past_shows_count"]=past_shows_count
  data["upcoming_shows_count"]=upcoming_shows_count
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  a=Artist.query.get(artist_id)
  form = ArtistForm(obj=a)
  artist={
    "id": a.id,
    "name": a.name,
    "genres": a.genres,
    "city": a.city,
    "state": a.state,
    "phone": a.phone,
    "website": a.website,
    "facebook_link": a.facebook_link,
    "seeking_venue": a.seeking_venue,
    "seeking_description": a.seeking_description,
    "image_link": a.image_link
  }
  # Done: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  name = request.form.get('name')
  city = request.form.get('city')
  state= request.form.get('state')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  website = request.form.get('website_link')
  seeking_venue = request.form.get('seeking_talent')
  seeking_description = request.form.get('seeking_description')
  try:
    artist = Artist.query.get(artist_id)
    artist.name=name
    artist.city=city
    artist.state=state
    artist.phone=phone
    artist.image_link=image_link
    artist.genres=genres
    artist.facebook_link=facebook_link
    artist.website=website
    artist.seeking_venue=seeking_venue
    artist.seeking_description=seeking_description
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
   db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  v=Venue.query.get(venue_id)
  form = VenueForm(obj=v)
  venue={
    "id": v.id,
    "name": v.name,
    "genres": v.genres,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website_link,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link
  }
  # Done: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  name = request.form.get('name')
  city = request.form.get('city')
  state= request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  website_link = request.form.get('website_link')
  seeking_talent = request.form.get('seeking_talent')
  seeking_description = request.form.get('seeking_description')
  print(name,city,state,address,phone)
  try:
    v = Venue.query.get(venue_id)
    v.name=name
    v.city=city
    v.state=state
    v.phone=phone
    v.image_link=image_link
    v.genres=genres
    v.facebook_link=facebook_link
    v.website_link=website_link
    v.seeking_talent=seeking_talent
    v.seeking_description=seeking_description
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except Exception as e:
   db.session.rollback()
   flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
   db.session.close()
  # Done: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  name = request.form.get('name')
  city = request.form.get('city')
  state= request.form.get('state')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  website = request.form.get('website_link')
  seeking_venue = request.form.get('seeking_talent')
  seeking_description = request.form.get('seeking_description')
 
  try:
    artist=Artist(name=name,city=city,state=state,phone=phone,image_link=image_link,genres=genres,
    facebook_link=facebook_link,website=website,seeking_venue=seeking_venue,seeking_description=seeking_description)
  # Done: insert form data as a new Venue record in the db, instead
    
   
    db.session.add(artist)
    # Done: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(sys.exc_info())
    print(traceback.format_exc())
    print(e)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
   # Done: on unsuccessful db insert, flash an error instead.
   # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
   db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows_in_database=show.query.all()
  print(shows_in_database)
  state_city=[]
  data=[]
  for s in shows_in_database:
    venue_name= s.venue.name
    artist_name=s.artist.name
    artist_image_link=s.artist.image_link
    data.append({
      "venue_id": s.venue_id,
      "venue_name": venue_name,
      "artist_id": s.artist_id,
      "artist_name": artist_name,
      "artist_image_link": artist_image_link,
      "start_time": str(s.start_time)
    })
    print(data)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  # Done: insert form data as a new Show record in the db, instead
  try:
    show1=show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
  # Done: insert form data as a new Venue record in the db, instead
    
   
    db.session.add(show1)
    # Done: modify data to be the data object returned from db insertion
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(sys.exc_info())
    print(traceback.format_exc())
    print(e)
    flash('An error occurred. Show could not be listed.')
   # Done: on unsuccessful db insert, flash an error instead.
   # e.g., flash('An error occurred. Show could not be listed.')
  finally:
   db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
