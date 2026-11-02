class Sensor :
    def __init__(self,
                 serialnumber: str,
                 TempTopic: str="",
                 HumiTopic: str="",
                 versTopic: str="",
                 dateTopic: str=""
                ):
        if int(serialnumber)<0:
            raise ValueError("numéro de serie invalide")
        self.serialnumber = serialnumber

        self.TempTopic = TempTopic or f"/iot/TEMPERATURE_{serialnumber}"
        self.HumiTopic = HumiTopic or f"/iot/HUMIDITY_{serialnumber}"
        self.versTopic = versTopic or f"/iot/VERSION_{serialnumber}"
        self.dateTopic = dateTopic or f"/iot/GET_DATE_{serialnumber}"
        
    def handleMessage(self,topic:str,message:str):
        if topic==self.TempTopic:
            #handleTemp
            return True
        elif topic== self.HumiTopic:
            #handleHumidity
            return True
        elif topic==self.versTopic:
            self.Version=message
            return True
        elif topic==self.dateTopic:
            #handleDate
            return True
        else:
            return False
