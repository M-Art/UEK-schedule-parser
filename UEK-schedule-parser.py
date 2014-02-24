#!/usr/bin/python

import codecs
from lxml import etree, html
from datetime import datetime

class ScheduleEntry(object):
    u"Represents the entry for schedule table."

    def __init__(self, dateFrom, dateTo, subject, subjectType, teacher, location):
        self.datesFromTo = [(dateFrom, dateTo)]
        self.dateTo = dateTo
        self.subject = subject
        self.subjectType = subjectType
        self.teacher = teacher
        self.location = location

    def toVEvent(self):
        datef = "%Y%m%dT%H%M%SZ"

        out = "BEGIN:VEVENT"
        for dateFromTo in self.datesFromTo:
            out += "\nDTSTART;TZID=Europe/Warsaw:" + dateFromTo[0].strftime(datef)
            out += "\nDTEND;TZID=Europe/Warsaw:" + dateFromTo[1].strftime(datef)
        out += "\nDESCRIPTION:" + self.teacher
        out += "\nLOCATION:" + self.location
        out += "\nSTATUS:CONFIRMED"
        prefix = "[W] " if self.subjectType == "wykład" else ""
        out += "\nSUMMARY:" + prefix + self.subject
        out += "\nEND:VEVENT"

        return out

def parseRowToScheduleEntry(fields):
    fields = [field.text for field in fields]
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

url = "http://planzajec.uek.krakow.pl/index.php?typ=G&id=69111&okres=1"
tree = html.parse(url)
rows = tree.xpath("//table/tr[count(td) = 6]")

for row in rows:
    fields = row.xpath("td")
    se = parseRowToScheduleEntry(fields)
    print(se.toVEvent())
