#!/usr/bin/python

import sys
import codecs
from lxml import etree, html
from datetime import datetime

class ScheduleEntry(object):
    u"Represents the entry for schedule table."

    def __init__(self, dateFrom, dateTo, subject, subjectType, teacher, location):
        xstr = lambda x: "" if x is None else x

        self.datesFromTo = [(dateFrom, dateTo)]
        self.dateTo = xstr(dateTo)
        self.subject = xstr(subject)
        self.subjectType = xstr(subjectType)
        self.teacher = xstr(teacher)
        self.location = xstr(location)

    def toVEvent(self):
        datef = "%Y%m%dT%H%M%SZ"

        out = "BEGIN:VEVENT"
        for dateFromTo in self.datesFromTo:
            out += "\nDTSTART;TZID=Europe/Warsaw:" + dateFromTo[0].strftime(datef)
            out += "\nDTEND;TZID=Europe/Warsaw:" + dateFromTo[1].strftime(datef)
        out += "\nDESCRIPTION:" + self.teacher
        out += "\nLOCATION:" + self.location
        out += "\nSTATUS:CONFIRMED"
        prefix = "[W] " if self.subjectType == u"wykład" else ""
        summary = self.subject if self.subject else self.subjectType
        out += "\nSUMMARY:" + prefix + summary
        out += "\nEND:VEVENT"

        return out

def parseRowToScheduleEntry(fields):
    dateBase = [int(f) for f in fields[0].split("-")]
    timeFrom = [int(f) for f in fields[1].split(" ")[1].split(":")]
    timeTo = [int(f) for f in fields[1].split(" ")[3].split(":")]

    dateFrom = datetime(dateBase[0], dateBase[1], dateBase[2], timeFrom[0], timeFrom[1])
    dateTo = datetime(dateBase[0], dateBase[1], dateBase[2], timeTo[0], timeTo[1])
    subject = fields[2]
    subjectType = fields[3]
    teacher = fields[4]
    location = fields[5]

    return ScheduleEntry(dateFrom, dateTo, subject, subjectType, teacher, location)

if len(sys.argv) < 2:
    print("Missing URL argument!")
    exit()

url = sys.argv[1]

try:
    tree = html.parse(url)
    rows = tree.xpath("//table/tr[count(td) = 6]")
    entries = []

    for row in rows:
        fields = [field.text for field in row.xpath("td")]

        entry = parseRowToScheduleEntry(fields)
        entries.append(entry)

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

    out = codecs.open("improved_schedule.ics", "w", "UTF-8")
    out.write(outString)
    out.close()

    print("Parsed " + str(len(entries)) + " events.")
except:
    print("Error!")
