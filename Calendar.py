from bs4 import BeautifulSoup as BS
from datetime import *
import pytz

TIMEZONE = pytz.timezone('Australia/Sydney')

firstDay = date(2019, 6, 3)

class Week():
    def __init__(self, monday, tuesday, wednesday, thursday, friday, saturday, sunday):
        self._monday = monday
        self._tuesday = tuesday
        self._wednesday = wednesday
        self._thursday = thursday
        self._friday = friday
        self._saturday = saturday
        self._sunday = sunday

    @property
    def monday(self):
        return self._monday

    @property
    def tuesday(self):
        return self._tuesday

    @property
    def wednesday(self):
        return self._wednesday

    @property
    def thursday(self):
        return self._thursday

    @property
    def friday(self):
        return self._friday

    @property
    def saturday(self):
        return self._saturday

    @property
    def sunday(self):
        return self._sunday

    def __str__(self):
        return (f"Monday:\n{self._monday}\n\n"
                f"Tuesday:\n{self._tuesday}\n\n"
                f"Wednesday:\n{self._wednesday}\n\n"
                f"Thursday:\n{self._thursday}\n\n"
                f"Friday:\n{self._friday}\n\n"
                f"Saturday:\n{self._saturday}\n\n"
                f"Sunday:\n{self._sunday}")


def getCalendar():
    soup = BS(open('calendar.html'), 'html.parser')
    calendarByWeek = {}

    table = soup.find('table')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        for i, col in enumerate(cols):
            ele = col.text.strip()
            # ele = ele.replace('\n', ' ')
            ele = ele.replace('<br />', '\n')
            # print(repr(ele))
            ele = ele.replace(' \xa0', ' and ')
            if i == 0:
                ele = ele.split('/ ')[1]
                calendarByWeek[ele] = []
                currentWeek = ele
            elif i > 2:
                if ele == '':
                    ele = "Nothing 🙌"
                elif ele == 'Coffee Night':
                    ele = 'Coffee Night ☕🖊️'
                calendarByWeek[currentWeek].append(ele)
    return calendarByWeek

def getWeek(weekNum):
    calendar = getCalendar()

    weekList = calendar['Week ' + str(weekNum)]

    week = Week(weekList[0], weekList[1], weekList[2], weekList[3], weekList[4], weekList[5], weekList[6])
    return week

def calculateWeekNum():
    currentDate = datetime.now(TIMEZONE).date()
    difference = (currentDate - firstDay).days
    numWeeks = int(difference/7) + 1
    return numWeeks


# print(getWeek(2))