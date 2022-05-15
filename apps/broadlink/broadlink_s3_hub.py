import appdaemon.plugins.hass.hassapi as hass
import broadlink


class BroadlinkS3Hub(hass.Hass):

    def initialize(self):
        self.entity_ids = self.args["entity_ids"]
        self.gangs: dict[str, int] = dict[str, int]()
        for i in range(len(self.entity_ids)):
            self.gangs.update({self.entity_ids[i]: i + 1})
        self.did = self.args["did"]
        self.scan_interval = self.args["scan_interval"]
        self.friendly_names = self.args["friendly_names"]
        self.device = broadlink.hello(self.args["hub_ip"])

        self.device.auth()
        self.listen_event(self.change_state, event="call_service")
        for i in range(len(self.entity_ids)):
            self._create_entity(index=i)
            self.run_in(self.handle_light_state, self.scan_interval, entity_id=self.entity_ids[i])

    def _create_entity(self, index):
        entity_id = self.entity_ids[index]
        self.log("Create entity with entity_id: '{entity_id}'".format(entity_id=entity_id))
        self.entity = self.get_ad_api().get_entity(entity_id)
        if self.entity.exists():
            self.remove_entity(entity_id)
        attributes = {"friendly_name": self.friendly_names[index]}
        state = self._get_device_state(entity_id=entity_id)
        self.entity.add(state=state, attributes=attributes)

    def handle_light_state(self, kwargs):
        entity_id = kwargs['entity_id']
        self.set_state(entity_id, state=self._get_device_state(entity_id=entity_id))
        self.run_in(self.handle_light_state, self.scan_interval, entity_id=entity_id)

    def _get_device_state(self, entity_id):
        gang = self.gangs[entity_id]
        state = self.device.get_state(self.did)
        entity_id = self.entity_ids[gang - 1]
        pwr = state["pwr{gang}".format(gang=gang)]
        if pwr == 1:
            self.log("Device state for entity: '{entity}', '{state}'".format(state="on", entity=entity_id))
            return "on"
        else:
            self.log("Device state for entity: '{entity}', '{state}'".format(state="off", entity=entity_id))
            return "off"

    def change_state(self, event_name, data, kwargs):
        data_entity_id = data["service_data"]["entity_id"]
        received_entity_ids = data_entity_id if isinstance(data_entity_id, list) else [data_entity_id]
        service = data["service"]
        for entity in received_entity_ids:
            if service == "turn_off" and entity in self.entity_ids:
                self._turn_entity_off(entity_id=entity)
            elif service == "turn_on" and entity in self.entity_ids:
                self._turn_entity_on(entity_id=entity)
            elif service == "toggle" and entity in self.entity_ids:
                if self._get_device_state(entity_id=entity) == "off":
                    self._turn_entity_on(entity_id=entity)
                else:
                    self._turn_entity_off(entity_id=entity)

    def _turn_entity_off(self, entity_id):
        self.log("Turn off '{entity}'".format(entity=entity_id))

        gang = self.gangs[entity_id]
        pwr = [None, None, None, None]
        pwr[gang] = 0
        self.device.set_state(self.did, pwr[1], pwr[2], pwr[3])
        self.set_state(entity_id, state="off")

    def _turn_entity_on(self, entity_id):
        self.log("Turn on '{entity}'".format(entity=entity_id))

        gang = self.gangs[entity_id]
        pwr = [None, None, None, None]
        pwr[gang] = 1
        self.device.set_state(self.did, pwr[1], pwr[2], pwr[3])
        self.set_state(entity_id, state="on")
