from src.models import City, Cinema, Movie, Show
from src.main import ma


class CitySchema(ma.SQLAlchemySchema):
    class Meta:
        model = City

    id = ma.auto_field()
    city_name = ma.auto_field()


class CinemaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Cinema

    name = ma.auto_field()
    show_times = ma.auto_field()


class MovieSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie

    id = ma.auto_field()
    name = ma.auto_field()


class ShowSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Show

    cinema_id = ma.Nested(CinemaSchema())
    show_times = ma.auto_field()
