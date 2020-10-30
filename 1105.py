# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        vars = ncs.template.Variables()
        DEVICE_NAME=service.hostname
        self.log.info('Device is %s' % DEVICE_NAME)
        vars.add('DEVICE_NAME', DEVICE_NAME)
        device_type_yang = root.devices.device[DEVICE_NAME].device_type.cli.ned_id
        #self.log.info('Device type is %s' % device_type_yang)
        if device_type_yang == "ios-id:cisco-ios":
            device_type = "cisco-xe"
        elif device_type_yang == "cisco-ios-xr-id:cisco-ios-xr":
            device_type = "cisco-xr"
        elif device_type_yang == "asa-id:cisco-asa":
            device_type = "cisco-asa"
        self.log.info('Device yang type is %s' % device_type_yang)
        self.log.info('Device type is %s' % device_type)
        return device_type
        self.config_SSH_device (tctx, root, service, DEVICE_NAME)

    def config_SSH_device(self, tctx, root, service, DEVICE_NAME):
        self.log.info("Running Pre-crypto config")
        self.pre_crypto_parameters (tctx, root, service, DEVICE_NAME)
        self.log.info("Running Post-crypto config")
        self.post_crypto_parameters (tctx, root, service, DEVICE_NAME)

    def pre_crypto_parameters(self, tctx, root, DEVICE_NAME):
        template = ncs.template.Template(service)
        if device_type == "cisco-xe":
            self.log.info("Applying XE template")
            template.apply('PRE-CRYPTO-XE-template', vars)
            device_cmd = root.devices.device[DEVICE_NAME].live_status.ios_stats__exec.any.get_input()
            self.log.info ('Device cmd is %s' % device_cmd)
            device_cmd.args = ["configure terminal"]
            output = root.devices.device[DEVICE_NAME].live_status.ios_stats__exec.any(device_cmd).result
            self.log.info ('Output is %s' % output)
            device_cmd = root.devices.device[DEVICE_NAME].live_status.ios_stats__exec.any.get_input()
            device_cmd.args = ["crypto key generate rsa | prompts 2048"]
            output= root.devices.device[DEVICE_NAME].live_status.ios_stats__exec.any(device_cmd).result
            self.log.info('Output is %s' % output)
        elif device_type == "cisco-xr":
            template.apply('SSH-CONFIG-XR-template', vars)
            self.log.info("Applying XR template")

    def post_crypto_parameters(self, tctx, root, service, DEVICE_NAME):
        template = ncs.template.Template(service)
        if device_type == "cisco-xe":
            self.log.info("Applying XE template")
            template.apply('POST-CRYPTO-XE-template', vars)
        elif device_type == "cisco-xr":
            template.apply('SSH-CONFIG-XR-template', vars)
            self.log.info("Applying XR template")

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('SSH-CONFIG-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
