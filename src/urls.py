from src.main import api
from src import resources

api.add_resource(resources.UserResource, '/user/')
api.add_resource(resources.UserLogin, '/user/login/')
api.add_resource(resources.CityResource, '/cities/')
api.add_resource(resources.MovieResource, '/movies/')
api.add_resource(resources.ShowResource, '/shows/')
api.add_resource(resources.TicketResource, '/tickets/')
