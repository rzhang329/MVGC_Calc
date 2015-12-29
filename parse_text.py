#!/usr/bin/python
import re
import json
import sys

class Parser:
    def __init__(self, name, str):
        self.course = {}
        self.course["Name"] = name
        data = str.splitlines()
        self.course["Holes"] = {"Par": [], "Men HCP": [], "Women HCP": []}
        self.course["Tees"] = {}
        for index, line in enumerate(data):
            if (re.match("Par", line)):
                self.course["Holes"]["Par"].extend(map(int, data[index + 1:index + 10]))
            if (re.match("HCP / Men", line)):
                self.course["Holes"]["Men HCP"].extend(map(int, data[index + 1:index + 10]))
            if (re.match("HCP / Women", line)):
                self.course["Holes"]["Women HCP"].extend(map(int, data[index + 1:index + 10]))
            if (re.match("Women", line)):
                count = index + 1
                while count < len(data):
                    self.parse_tee(self.course["Tees"], data[count:count + 3])
                    count += 3

    def parse_tee(self, tee, data):
        tee[data[0]] = {}
        if (data[1][0] != '-'):
            tee[data[0]]["Men"] = {}
            men_data = data[1].split(" / ")
            tee[data[0]]["Men"]["Rating"] = float(men_data[0])
            tee[data[0]]["Men"]["Slope"] = float(men_data[1])
        if (data[2][0] != '-'):
            tee[data[0]]["Women"] = {}
            women_data = data[2].split(" / ")
            tee[data[0]]["Women"]["Rating"] = float(women_data[0])
            tee[data[0]]["Women"]["Slope"] = float(women_data[1])

    def get_course(self):
        return self.course

if __name__ == "__main__":
    course_file = open(sys.argv[1], 'r')
    course_data = Parser(course_file.read()).get_course()
    print(json.dumps(course_data, indent=4))
