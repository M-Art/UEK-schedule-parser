import codecs
import urllib.request
from html.parser import HTMLParser

class ScheduleHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, True)
        self.__collecting__ = False
        self.__event__ = []
        self.__data__ = ""
        self.events = []
    def handle_starttag(self, tag, attrs):
        if tag == "td" and ("class", "termin") in attrs:
            self.__collecting__ = True
            
    def handle_data(self, data):
        if data.strip() == "":
            return
        if self.__collecting__ == True:
             self.__data__ = data.strip()
             
    def handle_endtag(self, tag):
        if self.__collecting__ == True and tag == "td":
            self.__event__.append(self.__data__)
            self.__data__ = ""
            if len(self.__event__) == 6:
                self.events.append(self.__event__)
                self.__collecting__ = False
                self.__event__ = []

def DTSTART(parts):
    d = parts[0].replace("-", "")
    t = parts[1].split("-")[0].strip()[3:].replace(":", "") + "00"
    return d + "T" + t + "Z"

def DTEND(parts):
    d = parts[0].replace("-", "")
    t = parts[1].split("-")[1].strip().replace(":", "") + "00"
    return d + "T" + t + "Z"

def DESCRIPTION(parts):
    return parts[4].strip()

def LOCATION(parts):
    return parts[5].strip()

def SUMMARY(parts):
    prefix = ""
    if parts[3].strip() == "wykład":
        prefix = "[W] "
    return prefix + parts[2].strip()

url = "http://planzajec.uek.krakow.pl/index.php?typ=G&id=69111&okres=1"
resp = urllib.request.urlopen(url).read()
content = resp.decode("UTF-8")

parser = ScheduleHTMLParser()
parser.feed(content)

outString = \
"""BEGIN:VCALENDAR
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
for event in parser.events:
    outString += "\nBEGIN:VEVENT"
    outString += "\nDTSTART;TZID=Europe/Warsaw:" + DTSTART(event)
    outString += "\nDTEND;TZID=Europe/Warsaw:" + DTEND(event)
    outString += "\nDESCRIPTION:" + DESCRIPTION(event)
    outString += "\nLOCATION:" + LOCATION(event)
    outString += "\nSTATUS:CONFIRMED"
    outString += "\nSUMMARY:" + SUMMARY(event)
    outString += "\nEND:VEVENT"
outString += "\nEND:VCALENDAR"

out = codecs.open("improved_schedule.ics", "w", "UTF-8")
out.write('\ufeff')
out.write(outString)
out.close()

print("done")
