from pyiot.zigbee import ZigbeeDevice, ZigbeeGateway
from pyiot.traits import OnOff

class SWTZ75(ZigbeeDevice, OnOff):
    """ TUYA Zigbee 3.0  1 gang Switch"""
    
    def __init__(self, sid:str, gateway:ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.add_alias('state', 'power')
        self.gateway.register_sub_device(self)
    
    def on(self):
        self.gateway.send_command(self.status.sid, 'state', 'on')
        
    def off(self):
         self.gateway.send_command(self.status.sid, 'state', 'off')
    
    def is_on(self) -> bool:
        return self.status.get('power') == "on"
    
    def is_off(self) -> bool:
        return self.status.get('power') == "off"