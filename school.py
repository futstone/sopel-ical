# coding=utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
from pytz import timezone
from datetime import datetime, timedelta
import sopel.module
from sopel.formatting import *
import io
from icalendar import Calendar, Event

days = ["MA", "TI", "KE", "TO", "PE", "LA", "SU"]


class Tapahtuma:
    def __init__(self, summary, location, dtstart, dtend):
        self.summary = summary[6:-7]
        self.location = location.split("/")
        self.yksikko = ""
        self.tila = ""
        if not location == "":
            self.location = location.split("/")
            self.tila = self.location[1]
            self.yksikko = self.location[0]
        else:
            self.tila = "AC"
            self.yksikko = "lesson"
        self.dtstart = dtstart.dt.astimezone(timezone("Europe/Helsinki"))
        self.dtend = dtend.dt.astimezone(timezone("Europe/Helsinki"))
        self.dt_date_month_year = datetime.strptime(self.dtstart.strftime("%d.%m.%Y"), "%d.%m.%Y")

    def getmsg(self):
        msg = color(days[self.dtstart.weekday()], colors.PURPLE) + " " + \
              color(str(self.dtstart.day) + ".", colors.BLUE) + \
              color(str(self.dtstart.month), colors.BLUE) + " " + \
              color(self.tila, colors.PURPLE) + " " + \
              color(self.yksikko, colors.BLUE) + " " + \
              color(str(self.dtstart.hour) + ":" + self.dtstart.strftime("%M") + " - " + str(self.dtend.hour) + ":" + self.dtend.strftime("%M"), colors.PURPLE) + " " + \
              color(self.summary, colors.BLUE)
        return msg


def parse_cal(filename):
    tapahtumat = []
    file = io.open(filename, 'r', encoding='utf-8')
    calendar = Calendar.from_ical(file.read())

    for ev in calendar.walk('vevent'):
        t = Tapahtuma(ev.get('summary'), ev.get('location'), ev.get('dtstart'), ev.get('dtend'))
        tapahtumat.append(t)

    # dn = timezone('Europe/Helsinki').localize(datetime.now())
    tapahtumat.sort(key = lambda x:x.dtstart)
    return tapahtumat


def select_tapahtumat(tapahtumat, jump):
    dates = []
    dt_date_month_year_now = datetime.strptime(datetime.now().strftime("%d.%m.%Y"), "%d.%m.%Y")
    selected_date = ""
    selected_tapahtumat = []

    for t in tapahtumat:
        if t.dt_date_month_year not in dates:
            dates.append(t.dt_date_month_year)

    for d in dates:
        if d >= dt_date_month_year_now:
            selected_date = d
            break

    index_of_selected_date = dates.index(selected_date) + jump

    if index_of_selected_date >= len(dates):
        index_of_selected_date = len(dates) - 1

    for t in tapahtumat:
        if t.dt_date_month_year == dates[index_of_selected_date]:
            selected_tapahtumat.append(t)

    return selected_tapahtumat


@sopel.module.commands("school")
def school(bot, trigger):
    jump = 0
    if trigger.group(2):
        if trigger.group(2).isdigit():
            jump = int(trigger.group(2))

    filename = "/home/futs/.sopel/rsc/kalenteri.txt"
    tapahtumat = parse_cal(filename)
    selected = select_tapahtumat(tapahtumat, abs(jump))

    for s in selected:
        bot.say(s.getmsg())