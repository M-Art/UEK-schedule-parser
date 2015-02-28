#!/usr/bin/python

import sys
import codecs
from lxml import etree, html
import datetime as dt

def secToPTHMS(total_sec):
    ret = "PT"

    m, s = divmod(total_sec, 60)
    h, m = divmod(m, 60)

    if h > 0:
        ret += str(int(h)) + "H"

    if h > 0 or m > 0:
        ret += str(int(m)) + "M"

    ret += str(int(s)) + "S"

    return ret

class ScheduleEntry(object):
    u"Represents the entry for schedule table."

    def __init__(self, dateTimeFrom, dateTimeTo, subject, subjectType, teacher, location):
        xstr = lambda x: "" if x is None else x

        self.dates = [(dateTimeFrom, dateTimeTo)]
        self.weekday = dateTimeFrom.weekday()
        self.startTime = dateTimeFrom.time()
        self.duration = dateTimeTo - dateTimeFrom
        self.subject = xstr(subject)
        self.subjectType = xstr(subjectType)
        self.teacher = xstr(teacher)
        self.location = xstr(location)

    def addDate(self, date):
        self.dates.append(date)

    def __eq__(self, other):
        return (self.weekday == other.weekday
            and self.startTime == other.startTime
            and self.duration == other.duration
            and self.subject == other.subject
            and self.subjectType == other.subjectType
            and self.teacher == other.teacher
            and self.location == other.location)

    def __hash__(self):
        return hash((
            self.weekday,
            self.startTime,
            self.duration,
            self.subject,
            self.subjectType,
            self.teacher,
            self.location))

    def toVEvent(self):
        datef = "%Y%m%dT%H%M%S"

        out = "BEGIN:VEVENT"
        out += "\nDTSTART;TZID=Europe/Warsaw:" + self.dates[0][0].strftime(datef)
        out += "\nDTEND;TZID=Europe/Warsaw:" + self.dates[0][1].strftime(datef)

        if len(self.dates) > 1:
            out += "\nRDATE;TZID=Europe/Warsaw:"
            out += ",".join([dateFrom.strftime(datef) for (dateFrom, _) in self.dates[1:]])

        out += "\nDESCRIPTION:" + self.teacher
        out += "\nLOCATION:" + self.location
        out += "\nSTATUS:CONFIRMED"
        prefix = "[W] " if self.subjectType == u"wykład" else ""
        summary = self.subject if self.subject else self.subjectType
        out += "\nSUMMARY:" + prefix + summary
        out += "\nEND:VEVENT"

        return out

def parseRowToScheduleEntry(fields):
    date = dt.date(*[int(f) for f in fields[0].split("-")])
    timeFrom = dt.time(*[int(f) for f in fields[1].split(" ")[1].split(":")])
    timeTo = dt.time(*[int(f) for f in fields[1].split(" ")[3].split(":")])

    dateTimeFrom = dt.datetime.combine(date, timeFrom)
    dateTimeTo = dt.datetime.combine(date, timeTo)
    subject = fields[2]
    subjectType = fields[3]
    teacher = fields[4]
    location = fields[5]

    return ScheduleEntry(dateTimeFrom, dateTimeTo, subject, subjectType, teacher, location)


url = raw_input("Enter URL with your schedule: ")

try:
    tree = html.parse(url)
    rows = tree.xpath("//table/tr[count(td) = 6]")
    entries = {} 

    for row in rows:
        fields = [field.text for field in row.xpath("td")]

        entry = parseRowToScheduleEntry(fields)

        if entry in entries:
            entries[entry].addDate(entry.dates[0])
        else:
            entries.update({entry:entry})

    outString = \
u"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Monika - plan zajęć
X-WR-TIMEZONE:Europe/Warsaw
X-WR-CALDESC:
BEGIN:VTIMEZONE
TZID:Europe/Warsaw
X-LIC-LOCATION:Europe/Warsaw
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE"""
    for entry in entries:
        outString += u"\n"
        outString += entry.toVEvent()
    outString += u"\nEND:VCALENDAR"

    print("Found " + str(len(entries)) + " different events")

    outFileName = "schedule.ics"

    out = codecs.open(outFileName, "w", "UTF-8")
    out.write(outString)
    out.close()

    print('Your schedule has been written to "' + outFileName + '" file')
except Exception as E:
    print("Error!")
