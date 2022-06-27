##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite.__main__
# @namespace Paperwrite.__main__
#
# Main package containing Main function of program, as well as all subpackages
# used in Paperwrite.

# -- LIBRARY
from waitress import serve

# -- PROJECT
from Paperwrite.Application import AppContext
from Paperwrite.PyAdditions import Io
from Paperwrite.RocketRouter import RocketRouter
from Paperwrite.Handlers.PostKngCreate import PostKngCreate
from Paperwrite.Handlers.GetKngList import GetKngList
from Paperwrite.Handlers.GetKngVisualisation import GetKngVisualisation
from Paperwrite.Handlers.GetKngDetails import GetKngDetails
from Paperwrite.Handlers.GetKngTrainModel import GetKngTrainModel
from Paperwrite.Handlers.PostKngPredict import PostKngPredict


##
# Main function of program. Refrenced in `setup.cfg` as `entry_point`. This
# function can be used for production.
def Main() -> None:
  # initializing router
  router = RocketRouter()

  # mount all routes to router
  router.Mount("/kng/list", GetKngList, ["GET"])
  router.Mount("/kng/{kid:str}/details", GetKngDetails, ["GET"])
  router.Mount("/kng/{kid:str}/visualisation.html", GetKngVisualisation,
               ["GET"])
  router.Mount("/kng/{kid:str}/create", PostKngCreate, ["POST"])
  router.Mount("/kng/{kid:str}/predict", PostKngPredict, ["POST"])
  router.Mount("/kng/{kid:str}/train_model", GetKngTrainModel, ["GET"])

  # build Flask provider from router
  provider = router.Build()

  # getting server information
  host = AppContext.Config.Webserver.Host
  port = AppContext.Config.Webserver.Port
  apiPrefix = AppContext.Config.Webserver.ApiPrefix
  # print out all routes, that will be served by Flask
  apiRoutes = [f"{apiPrefix}{r}" for r in router.GetRoutes()]
  Io.Info(f"Serving API at http://{host}:{port}")
  for r in apiRoutes:
    Io.Info(f"    => {r}")

  # server Flask with waitress
  serve(provider, host=host, port=port)


# Python Main
if __name__ == "__main__":
  Main()