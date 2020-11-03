from pyiot.zigbee import ZigbeeDevice, ZigbeeGateway
from pyiot.traits import MotionStatus

class SNZB03(ZigbeeDevice, MotionStatus):
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)