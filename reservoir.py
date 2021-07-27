from typing import Any, Dict, Union
import pydantic
import requests
from bs4 import BeautifulSoup


class PayLoad(pydantic.BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    view_state: str
    view_state_generator: str
    event_validation: str

    @pydantic.validator("minute")
    @classmethod
    def is_minute(cls, value) -> None:
        assert value in {
            0,
            10,
            20,
            30,
            40,
            50,
        }, f"{value} not in {[0, 10, 20, 30, 40, 50]}"

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "ctl00$ctl02": "ctl00$cphMain$ctl00|ctl00$cphMain$btnQuery",
            "ctl00_ctl02_HiddenField": ";;AjaxControlToolkit, Version=3.0.20820.16598, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:zh-TW:707835dd-fa4b-41d1-89e7-6df5d518ffb5:411fea1c:865923e8:77c58d20:91bd373d:14b56adc:596d588c:8e72a662:acd642d2:269a19ae",
            "__EVENTTARGET": "ctl00$cphMain$btnQuery",
            "__EVENTARGUMENT": "",
            "ctl00$cphMain$cboSearch": "防汛重點水庫",
            "ctl00$cphMain$ucDate$cboYear": self.year,
            "ctl00$cphMain$ucDate$cboMonth": self.month,
            "ctl00$cphMain$ucDate$cboDay": self.day,
            "ctl00$cphMain$ucDate$cboHour": self.hour,
            "ctl00$cphMain$ucDate$cboMinute": self.minute,
            "__VIEWSTATE": self.view_state,
            "__VIEWSTATEGENERATOR": self.view_state_generator,
            "__EVENTVALIDATION": self.event_validation,
            "__ASYNCPOST": True,
        }
        return payload
    
    class Config:
        allow_mutation = False


class ReservoirSession:
    def __init__(self) -> None:
        self.session = requests.session()
        self.url = "https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx"

    def fetch_aspx_state(self) -> None:
        page = self.session.get("https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx")
        soup = BeautifulSoup(page.text, "html")
        self.view_state = soup.find(id="__VIEWSTATE")["value"]
        self.event_validation = soup.find(id="__EVENTVALIDATION")["value"]
        self.view_state_generator = soup.find(id="__VIEWSTATEGENERATOR")[
            "value"
        ]

    def fetch_page(self, year: int, month: int, day: int, hour: int, minute: int) -> str:
        payload = PayLoad(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            view_state=self.view_state,
            view_state_generator=self.view_state_generator,
            event_validation=self.event_validation,
        )
        post_result = self.session.post(self.url, data=payload.to_dict())
        return post_result.text

if __name__ == "__main__":
    import pandas as pd
    session = ReservoirSession()
    session.fetch_aspx_state()
    page = session.fetch_page(2020, 10, 5, 23, 10)
    print(pd.read_html(page)[0])
