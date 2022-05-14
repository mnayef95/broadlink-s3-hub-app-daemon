import appdaemon.plugins.hass.hassapi as hass
import broadlink


class BroadlinkS3Hub(hass.Hass):

    def initialize(self):
        self.entity_ids = self.args["entity_ids"]
        self.did = self.args["did"]
        self.scan_interval = self.args["scan_interval"]
        self.friendly_names = self.args["friendly_names"]
        self.device = broadlink.hello(self.args["hub_ip"])

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
        entity_id = self.entity_ids[gang - 1]
        self.set_state(entity_id, state=self._get_device_state(gang=gang))
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
        data_entity_id = data["service_data"]["entity_id"]
        received_entity_id = data_entity_id[0] if isinstance(data_entity_id, list) else data_entity_id
        gang = kwargs["gang"]
        entity_id = self.entity_ids[gang - 1]

        if data["service"] == "turn_off" and received_entity_id == entity_id:
            self._turn_entity_off(gang=gang)
        elif data["service"] == "turn_on" and received_entity_id == entity_id:
            self._turn_entity_on(gang=gang)

    def _turn_entity_off(self, gang):
        entity_id = self.entity_ids[gang - 1]
        self.log("Turn off '{entity}'".format(entity=entity_id))
        pwr = [None, None, None, None]
        pwr[gang] = 0
        self.device.set_state(self.did, pwr[1], pwr[2], pwr[3])
        self.set_state(entity_id, state="off")

    def _turn_entity_on(self, gang):
        entity_id = self.entity_ids[gang - 1]
        self.log("Turn on '{entity}'".format(entity=entity_id))
        pwr = [None, None, None, None]
        pwr[gang] = 1
        self.device.set_state(self.did, pwr[1], pwr[2], pwr[3])
        self.set_state(entity_id, state="on")
