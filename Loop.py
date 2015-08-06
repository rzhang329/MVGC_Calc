#!/usr/bin/python

import os

def CreateHTML:
    playerFile = open("mvgc_player_ghin.txt")
    outputFile = open("Players.html", 'w')
    players = []
    outputFile.write('<br><select name="people">\n')
    outputFile.write('<option value="none"></option>')
    for line in playerFile.read().splitlines():
        ghin,name = line.split("\t")
        name = ''.join(name.split('\"'))
        players.append(name)
    players.sort()
    for name in players:
        element = '<option value="' + name + '">' + name + "</option>\n"
        outputFile.write(element)
    outputFile.write('</select><br>')
    playerFile.close()
    outputFile.close()
    courseFile = open("mvgc_course_index.txt")
    outputFile = open("Courses.html", 'w')
    courses = []
    outputFile.write('<br><select name="places">\n')
    for line in courseFile.read().splitlines():
        name,tee,slope = line.split("\t")
        courses.append(name)
    courses.sort()
    for name in courses:
        element = '<option value="' + name + '">' + name + "</option>\n"
        outputFile.write(element)
    outputFile.write('</select>')
    courseFile.close()
    outputFile.close()

CreateHTML()
