from oslo_config import cfg
from pecan import hooks

from shadowfiend.common import context
from shadowfiend.conductor import api as conductor_api
from shadowfiend.processor import api as processor_api

CONF = cfg.CONF
CONF.import_opt('auth_uri', 'keystonemiddleware.auth_token',
                group='keystone_authtoken')


class ContextHook(hooks.PecanHook):
    """Configures a request context and attaches it to the request.

    The following HTTP request headers are used:

    X-User-Name:
        Used for context.user_name.

    X-User-Id:
        Used for context.user_id.

    X-Project-Name:
        Used for context.project.

    X-Project-Id:
        Used for context.project_id.

    X-Auth-Token:
        Used for context.auth_token.

    X-Roles:
        Used for context.roles.
    """

    def before(self, state):
        headers = state.request.headers
        user_name = headers.get('X-User-Name')
        user_id = headers.get('X-User-Id')
        project = headers.get('X-Project-Name')
        project_id = headers.get('X-Project-Id')
        domain_id = headers.get('X-User-Domain-Id')
        domain_name = headers.get('X-User-Domain-Name')
        auth_token = headers.get('X-Auth-Token')
        roles = headers.get('X-Roles', '').split(',')
        auth_token_info = state.request.environ.get('keystone.token_info')

        auth_url = CONF.keystone_authtoken.auth_uri

        state.request.context = context.make_context(
            auth_token=auth_token,
            auth_url=auth_url,
            auth_token_info=auth_token_info,
            user_name=user_name,
            user_id=user_id,
            project_name=project,
            project_id=project_id,
            domain_id=domain_id,
            domain_name=domain_name,
            roles=roles)


class RPCHook(hooks.PecanHook):
    """Attach the rpcapi object to the request so controllers can get to it."""

    def before(self, state):
        state.request.conductor_rpcapi = conductor_api.API(context=state.request.context)
        state.request.processor_rpcapi = processor_api.API(context=state.request.context)
