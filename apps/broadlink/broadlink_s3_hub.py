import appdaemon.plugins.hass.hassapi as hass
import broadlink


class BroadlinkS3Hub(hass.Hass):

    def initialize(self):
        self.entity_ids = self.args["entity_ids"]
        self.did = self.args["did"]
        self.scan_interval = self.args["scan_interval"]
        self.friendly_names = self.args["friendly_names"]
        self.device = broadlink.hello(self.args["hub_ip"])

        self.log("Device: '{device}'".format(device=self.device))
        self.device.auth()
        for i in range(len(self.entity_ids)):
            self._create_entity(index=i)
            self.listen_event(self.change_state, event="call_service", gang=i + 1)
            self.run_in(self.handle_light_state, self.scan_interval, gang=i + 1)

    def _create_entity(self, index):
        entity_id = self.entity_ids[index]
        self.log("Create entity with entity_id: '{entity_id}'".format(entity_id=entity_id))
        self.entity = self.get_ad_api().get_entity(entity_id)
        if self.entity.exists():
            self.remove_entity(entity_id)
        attributes = {"friendly_name": self.friendly_names[index]}
        state = self._get_device_state(gang=index + 1)
        self.entity.add(state=state, attributes=attributes)

    def handle_light_state(self, kwargs):
        gang = kwargs['gang']
        self.entity.set_state(state=self._get_device_state(gang=gang))
        self.run_in(self.handle_light_state, self.scan_interval, gang=gang)

    def _get_device_state(self, gang):
        state = self.device.get_state(self.did)
        pwr = state["pwr{gang}".format(gang=gang)]
        if pwr == 1:
            self.log("Device state: '{state}'".format(state="on"))
            return "on"
        else:
            self.log("Device state: '{state}'".format(state="off"))
            return "off"

    def change_state(self, event_name, data, kwargs):
        gang = kwargs["gang"]
        entity_id = self.entity_ids[gang - 1]
        recived_entity_id = None
        if isinstance(data["service_data"]["entity_id"], list):
            recived_entity_id = data["service_data"]["entity_id"][0]
        else:
            recived_entity_id = data["service_data"]["entity_id"]
        pwr = [None, None, None, None]
        self.log("Change state: '{event_name}'".format(event_name=event_name))
        self.log("Call service: '{service}'".format(service=data["service"]))
        self.log("Data entity id: '{entity_id}'".format(entity_id=recived_entity_id))
        self.log("Entity id: '{entity_id}'".format(entity_id=entity_id))
        if data["service"] == "turn_off" and recived_entity_id == entity_id:
            self.log("Turn off '{entity}'".format(entity=entity_id))
            pwr[gang] = 0
            self.device.set_state(self.did, pwr[1], pwr[2], pwr[3])
            self.entity.set_state(state="off")
        elif data["service"] == "turn_on" and recived_entity_id == entity_id:
            self.log("Turn on '{entity}'".format(entity=entity_id))
            pwr[gang] = 1
            self.device.set_state(self.did, pwr[1], pwr[2], pwr[3])
            self.entity.set_state(state="on")
