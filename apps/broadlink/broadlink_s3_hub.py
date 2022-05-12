import appdaemon.plugins.hass.hassapi as hass
import json
import broadlink

from threading import Thread
from time import sleep

class BroadlinkS3Hub(hass.Hass):

    def initialize(self):
        self.entity_id = self.args["entity_id"]
        self.did = self.args["did"]
        self.gang = self.args["gang"]
        self.scan_interval = self.args["scan_interval"]
        self.device = broadlink.hello(self.args["hub_ip"])

        self.device.auth()
        self.listen_event(self.change_state, event = "call_service")
        self.handle = self.run_in(self.handle_light_state, self.scan_interval)

    def handle_light_state(self, *kwargs):
        state = self.device.get_state(self.did)
        pwr = state["pwr{gang}".format(gang = self.gang)]
        self.log("Device pwr value is: '{pwr}'".format(pwr = pwr))
        if pwr == 1:
            self.set_state(self.entity_id, state = "on")
        else:
            self.set_state(self.entity_id, state = "off")
        self.handle = self.run_in(self.handle_light_state, self.scan_interval)
    
    def change_state(self, event_name, data, kwargs):
        pwr = [None, None, None, None]
        if(data["service"] == "turn_off" and data["service_data"]["entity_id"] == self.entity_id):
            self.log("Turn off '{entity}'".format(entity=self.entity_id))
            pwr[self.gang] = 0
            self.device.set_state(self.did, pwr[1], pwr[2], pwr[3])
            self.set_state(self.entity_id, state = "off")
        elif(data["service"] == "turn_on" and data["service_data"]["entity_id"] == self.entity_id):
            self.log("Turn on '{entity}'".format(entity=self.entity_id))
            pwr[self.gang] = 1
            self.device.set_state(self.did, pwr[1], pwr[2], pwr[3])
            self.set_state(self.entity_id, state = "on")
    
    def terminate(self):
        self.cancel_timer(self.handle)
