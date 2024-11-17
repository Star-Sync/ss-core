import datetime
from app.entities import Satellite


class RFTime():
    '''
    This is the first type of request. It is more general since user only specifies the satellite and start/end times for which the contact should happen.
    '''
    def __init__(
            self, 
            mission: str, 
            satellite: Satellite, 
            start_time: datetime, 
            end_time: datetime, 
            uplink: float, 
            downlink: float, 
            science: float, 
            pass_num: int = 1):
        self.mission = mission
        self.satellite = satellite
        self.start_time = start_time
        self.end_time = end_time
        self.uplink = uplink
        self.telemetry = downlink
        self.science = science
        self.passNum = pass_num
        self.timeRemaining = max(self.uplink, self.telemetry, self.science)
        self.passNumRemaining = pass_num

    def get_priority_weight(self) -> int:
        tot_time = self.uplink + self.telemetry + self.science
        time_period = self.end_time - self.start_time
        
        return (self.end_time - datetime.now()).total_seconds()*(tot_time/time_period.total_seconds())
    
    def set_time_remaining(self, time_booked: int) -> int:
        self.timeRemaining = self.timeRemaining - time_booked
    
    def decrease_pass(self):
        self.passNumRemaining -= 1