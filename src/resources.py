"""
File where we create API resources
"""
import traceback
from datetime import datetime

from flask import request
from flask_jwt_extended import (create_refresh_token,
                                jwt_refresh_token_required, get_jwt_identity)
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError

from src.main import logger, db
from src.models import User, City, Movie, Cinema, Show, Ticket
from src.schemas import CitySchema, MovieSchema


class UserLogin(Resource):
    """
    Restful resource for logging in user
    """

    parser = reqparse.RequestParser()

    def post(self):

        # adding arguments to data parser for required
        # fields
        self.parser.add_argument('phone_number',
                                 help='Phone number cannot be blank',
                                 required=True)
        self.parser.add_argument('password',
                                 help='Password cannot be blank',
                                 required=True)

        data = self.parser.parse_args(strict=True)

        user = User.query.filter_by(phone_number=data["phone_number"]).first()

        if not user:
            logger.info(
                "request from {0} to {1} failed because of wrong phone number/"
                "unregistered number ({2}) is entered.".format(
                    request.remote_addr, request.path, data["phone_number"]))
            return {
                'message':
                'Please check your phone number {0}/ If not registered, '
                'kindly register with us.'.format(data["phone_number"])
            }, 401

        if user.check_password(data["password"], user.password):
            logger.info(
                "request from {0} for user login request is successful for "
                "phone number {1}".format(request.remote_addr,
                                          data["phone_number"]))
            db.session.commit()
            refresh_token = create_refresh_token({
                "id": user.id,
            })
            return {
                'message': 'Logged in as {0}'.format(data["phone_number"]),
                'refresh_token': refresh_token
            }, 200
        else:
            logger.info(
                "request from {0} for user login request is failed for "
                "phone number {1} because of wrong password.".format(
                    request.remote_addr, data["phone_number"]))
            return {'message': 'Kindly check your password.'}, 404


class UserResource(Resource):
    """
    Resource for creating user
    """

    parser = reqparse.RequestParser()

    def post(self):

        self.parser.add_argument('phone_number',
                                 help='Phone number cannot be blank',
                                 required=True)
        self.parser.add_argument('password',
                                 help='Password cannot be blank',
                                 required=True)

        data = self.parser.parse_args(strict=True)

        user = User.query.filter_by(phone_number=data["phone_number"]).first()

        if user:
            return {
                "data": {
                    "error_message": "Phone number already exists"
                }
            }, 409
        else:
            new_user = User(**data)
            new_user.pre_commit_setup()
            try:
                db.session.add(new_user)
                db.session.commit()
            except IntegrityError:
                return {
                    "data": {
                        "error_message": "Phone number already exists"
                    }
                }, 409
            return {
                "data": {
                    "success_message": "User created successfully.",
                    "phone_number": data["phone_number"]
                }
            }, 201


class CityResource(Resource):
    """
    Resource for city
    """
    def get(self):

        try:
            cities = City.query.all()
            city_schema = CitySchema(many=True)
            return {"data": city_schema.dump(cities)}, 200
        except Exception:
            logger.error(
                f"Error while querying cities {traceback.format_exc()}")


class MovieResource(Resource):
    """
    Resource for Movie
    """

    parser = reqparse.RequestParser()

    def get(self):
        self.parser.add_argument('city_id', location='args')
        data = self.parser.parse_args()

        city = City.query.filter_by(id=data['city_id']).first()
        movies = city.movies
        movie_schema = MovieSchema(many=True)
        return {"data": movie_schema.dump(movies)}, 200


class ShowResource(Resource):
    """
    Resource for Cinema
    """
    parser = reqparse.RequestParser()

    def get(self):
        self.parser.add_argument('movie_id', location='args')
        self.parser.add_argument('cinema_id', location='args')
        self.parser.add_argument('show_time', location='args')
        self.parser.add_argument('show_date', location='args')

        data = self.parser.parse_args()
        shows = Show.query.join(Movie).join(Cinema).filter(
            Show.movie_id == data['movie_id'])

        if data["cinema_id"]:
            shows = shows.filter(Show.cinema_id == data["cinema_id"])
        if data["show_time"]:
            shows = shows.filter(Show.show_times == data["show_time"])
        if data["show_date"]:
            show_date = datetime.strptime(data["show_date"], "%d-%m-%Y").date()
            shows = shows.filter(Show.show_date == show_date)
        shows = shows.all()
        response = {}
        for show in shows:
            if show.cinema.name in response:
                response[show.cinema.name]["show_times"].append({
                    "show_time":
                    show.show_times,
                    "available_seats":
                    show.no_of_seats,
                    "show_date":
                    show.show_date.strftime("%d-%m-%Y")
                })

            else:
                response[show.cinema.name] = {
                    "cinema":
                    show.cinema.name,
                    "show_times": [{
                        "show_time":
                        show.show_times,
                        "available_seats":
                        show.no_of_seats,
                        "show_date":
                        show.show_date.strftime("%d-%m-%Y")
                    }]
                }
        return {"data": list(response.values())}, 200


class TicketResource(Resource):
    """
    Resource for tickets
    """

    parser = reqparse.RequestParser()

    @jwt_refresh_token_required
    def post(self):
        self.parser.add_argument('movie_id',
                                 required=True,
                                 help='movie id is mandatory',
                                 location='json',
                                 dest='movie')
        self.parser.add_argument('cinema_id',
                                 required=True,
                                 help='cinema id is mandatory',
                                 location='json',
                                 dest='cinema')
        self.parser.add_argument('show_time',
                                 required=True,
                                 help='show time is mandatory',
                                 location='json')
        self.parser.add_argument('no_of_seats',
                                 required=True,
                                 type=int,
                                 help='number of tickets is mandatory',
                                 location='json')
        self.parser.add_argument('ticket_date',
                                 required=True,
                                 help='Ticket date is mandatory',
                                 location='json')

        data = self.parser.parse_args(strict=True)
        data["user"] = get_jwt_identity()["id"]
        data["ticket_date"] = datetime.strptime(data["ticket_date"],
                                                "%d-%m-%Y")
        show = Show.query.filter_by(movie_id=data["movie"],
                                    cinema_id=data["cinema"],
                                    show_times=data["show_time"],
                                    show_date=data["ticket_date"]).first()
        if not show:
            return {
                "data": {
                    "error_message":
                    "No show available for selected Movie/Cinema/Date"
                }
            }, 404
        else:
            if not show.no_of_seats >= data["no_of_seats"]:
                return {
                    "data": {
                        "error_message":
                        "No tickets are available for selected data"
                    }
                }, 404
            else:
                try:
                    show.no_of_tickets = show.no_of_seats - data["no_of_seats"]
                    db.session.commit()
                    ticket = Ticket(**data)
                    ticket.pre_commit_setup()
                    db.session.add(ticket)
                    db.session.commit()
                    return {
                        "data": {
                            "success_message": "Ticket booked successfully"
                        }
                    }
                except Exception:
                    db.session.rollback()
                    logger.error(
                        f"Error while booking tickets {traceback.format_exc()}"
                    )
                    return {
                        "data": {
                            "error_message":
                            "Unexpected error occurred. Try again later."
                        }
                    }
