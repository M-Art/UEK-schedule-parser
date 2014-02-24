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

    def addDateFromTo(self, dateFromTo):
        self.datesFromTo.append(dateFromTo)

    def __eq__(self, other):
        return (self.subject == other.subject
            and self.subjectType == other.subjectType
            and self.teacher == other.teacher
            and self.location == other.location)

    def __hash__(self):
        return hash((
            self.subject,
            self.subjectType,
            self.teacher,
            self.location))

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

url = "http://planzajec.uek.krakow.pl/index.php?typ=G&id=69111&okres=1"
tree = html.parse(url)
rows = tree.xpath("//table/tr[count(td) = 6]")
entries = {}

for row in rows:
    fields = [field.text for field in row.xpath("td")]

    entry = parseRowToScheduleEntry(fields)
    if entry in entries:
        entries[entry].addDateFromTo(entry.datesFromTo[0])
    else:
        entries.update({entry:entry})

for entry in entries:
    print(entry.toVEvent())

