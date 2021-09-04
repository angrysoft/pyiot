from pyiot.zigbee import ZigbeeDevice, ZigbeeGateway
from pyiot.traits import Contact, MotionStatus

class SNZB01(ZigbeeDevice):
    def __init__(self, sid: str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)


class SNZB02(ZigbeeDevice, Contact):
    def __init__(self, sid: str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)
    
    def is_open(self) -> bool:
        return not self.status.contact
    
    def is_close(self) -> bool:
        return self.status.contact
    

class SNZB03(ZigbeeDevice, MotionStatus):
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)