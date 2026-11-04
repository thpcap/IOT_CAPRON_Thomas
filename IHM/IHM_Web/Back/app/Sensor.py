from pydantic import BaseModel

class Sensor:

    def __init__(
        self,
        serialnumber: str,
        id: int | None = None,
        TempTopic: str = "",
        HumiTopic: str = "",
        versTopic: str = "",
        dateTopic: str = "",
        CommandTopic: str = "",
        BlinkTopic: str = "",
        BargraphTopic: str = ""
    ):

        if not serialnumber.isdigit():
            raise ValueError("Numéro de série invalide")

        self.serialnumber = serialnumber
        self.id = id
        self.TempTopic = TempTopic or f"/iot/TEMPERATURE_{serialnumber}"
        self.HumiTopic = HumiTopic or f"/iot/HUMIDITY_{serialnumber}"
        self.versTopic = versTopic or f"/iot/VERSION_{serialnumber}"
        self.dateTopic = dateTopic or f"/iot/GET_DATE_{serialnumber}"

        self.CommandTopic = CommandTopic or f"/iot/COMMAND_{serialnumber}"
        self.BlinkTopic = BlinkTopic or f"/iot/BLINK_{serialnumber}"
        self.BargraphTopic = BargraphTopic or f"/iot/BARGRAPH_{serialnumber}"
        
class SensorCreate(BaseModel):
    serialnumber: str
    name: str | None = None
    TempTopic: str | None = "",
    HumiTopic: str | None = "",
    versTopic: str | None = "",
    dateTopic: str | None = "",
    CommandTopic: str | None = "",
    BlinkTopic: str | None = "",
    BargraphTopic: str | None = ""

class SendCommandRequest(BaseModel):
    capteurs: list[str]
    commande: str
    value: str | None = None