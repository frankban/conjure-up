from conjure.ui.views.cloud import CloudView
from conjure import async
from conjure import utils
from conjure import controllers
from conjure.app_config import app
from conjure import juju
import petname
from . import common


class CloudsController:
    def __init__(self):
        self.view = None

    def __handle_exception(self, exc):
        utils.pollinate(app.session_id, "E004")
        app.ui.show_exception_message(exc)

    def __add_model(self):
        juju.switch_controller(app.current_controller)
        juju.add_model(app.current_model)
        juju.switch_model(app.current_model)

    def finish(self, cloud):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        cloud: Cloud to create the controller/model on.
        """
        utils.pollinate(app.session_id, 'CS')
        existing_controller = common.get_controller_in_cloud(cloud)

        if existing_controller is None:
            return controllers.use('newcloud').render(cloud)

        app.current_controller = existing_controller
        app.current_model = petname.Name()
        async.submit(self.__add_model,
                     self.__handle_exception,
                     queue_name=juju.JUJU_ASYNC_QUEUE)

        # Go through the rest of the gui since we already provide a direct
        # spell path
        if app.fetcher != 'charmstore-search':
            return controllers.use('bundlereadme').render()
        return controllers.use('variants').render()

    def render(self):
        clouds = common.list_clouds()
        excerpt = app.config.get(
            'description',
            "Please select from a list of available clouds")
        view = CloudView(app,
                         clouds,
                         self.finish)

        app.ui.set_header(
            title="Choose a Cloud",
            excerpt=excerpt
        )
        app.ui.set_body(view)


_controller_class = CloudsController
