import uuid
from datetime import datetime
from itertools import chain

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from passlib.hash import django_pbkdf2_sha256

from src.main import db


class User(db.Model):
    """
    User model for storing user data
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    tickets = db.relationship("Ticket")

    @classmethod
    def check_password(cls, password, _hash):
        return django_pbkdf2_sha256.verify(password, _hash)

    def pre_commit_setup(self):
        """
        This method generates the required fields either from available
        information else automatic fields are generated.
        """
        self.password = django_pbkdf2_sha256.hash(self.password)


class City(db.Model):
    """
    List of cities  which are playing movies
    """
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(80), nullable=False)
    cinemas = db.relationship("Cinema")

    @hybrid_property
    def movies(self):
        return list(chain(*[cinema.movies for cinema in self.cinemas]))


class Show(db.Model):
    __tablename__ = "shows"
    movie_id = db.Column(db.Integer,
                         db.ForeignKey('movies.id'),
                         primary_key=True)
    cinema_id = db.Column(db.Integer,
                          db.ForeignKey('cinemas.id'),
                          primary_key=True)
    show_times = db.Column(db.String(8), nullable=False, primary_key=True)
    show_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    no_of_seats = db.Column('no_of_seats', db.Integer, nullable=False)
    cinema = db.relationship("Cinema", backref="shows")


class Movie(db.Model):
    """
    Model form movie details
    """
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    release_date = db.Column(db.DateTime)
    cinemas = db.relationship("Cinema",
                              secondary='shows',
                              back_populates="movies")


class Cinema(db.Model):
    """
    Model for cinemas
    """
    __tablename__ = "cinemas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    show_times = db.Column(ARRAY(db.String(8)))
    city = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    movies = db.relationship("Movie",
                             secondary='shows',
                             back_populates="cinemas")


class Ticket(db.Model):
    """
    Model for tickets
    """

    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(128), nullable=False)
    movie = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    cinema = db.Column(db.Integer, db.ForeignKey('cinemas.id'), nullable=False)
    show_time = db.Column(db.String(8), nullable=False)
    no_of_seats = db.Column(db.Integer, nullable=False)
    ticket_date = db.Column(db.Date, nullable=False)
    transaction_date = db.Column(db.Date,
                                 nullable=False,
                                 default=datetime.utcnow)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def pre_commit_setup(self):
        """
        This method is used to generate uuids for each ticket transaction.
        """

        self.transaction_id = uuid.uuid1()
