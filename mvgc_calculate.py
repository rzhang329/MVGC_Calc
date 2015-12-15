#!/usr/bin/python

import os,re
import BeautifulSoup
import urllib
from google.appengine.ext import ndb

class Player(ndb.Model):
    name = ndb.StringProperty()
    ghin = ndb.StringProperty()

class Course(ndb.Model):
    name = ndb.StringProperty()
    tee = ndb.StringProperty()
    slope = ndb.StringProperty()

class LCourse(ndb.Model):
    name = ndb.StringProperty()
    tee = ndb.StringProperty()
    slope = ndb.StringProperty()
    lady_rate = ndb.StringProperty()
    man_rate = ndb.StringProperty()

def read_player_data(key_name):
    dd = {}
    key = ndb.Key("MVGC_Data", key_name)
    player_list = Player.query(ancestor=key).fetch()
    for item in player_list:
        dd[item.name] = item.ghin
    return dd

def read_course_data():
    dd = {}
    key = ndb.Key("MVGC_Data", "courses")
    course_list = Course.query(ancestor=key).fetch()
    for item in course_list:
        dd[item.name] = (item.tee,item.slope)
    return dd

def read_lady_course_file():
    dd = {}
    key = ndb.Key("MVGC_Data", "lady_courses")
    course_list = LCourse.query(ancestor=key).fetch()
    for x in course_list:
        dd[x.name] = (x.tee,x.slope,x.lady_rate,x.man_rate)
    return dd

def read_lady_data():
    dd = set()
    key = ndb.Key("MVGC_Data", "ladies")
    lady_list = Player.query(ancestor=key).fetch()
    for item in lady_list:
        dd.add(item.name)
    return dd

def lookup_index(ghin):
    url = 'http://widgets.ghin.com/HandicapLookupResults.aspx?ghinno=%s' % ghin
    page = urllib.urlopen(url)
    ss = BeautifulSoup.BeautifulSoup(page.read())
    ind_str = ss.find('td', {'class' : 'ClubGridHandicapIndex'}).text
#    print 'Index for %s is: %s' % (ghin, ind_str)

    while ind_str and ind_str[len(ind_str)-1].isdigit() is False:
        ind_str = ind_str[:len(ind_str)-1]
        
    if not ind_str:
        return 0.0
    return float(ind_str)

def get_esc(p_ci):
    if p_ci >= 40:
        esc = '10'
    else:
        if p_ci >= 30:
            esc = '9'
        else:
            if p_ci >= 20:
                esc = '8'
            else:
                if p_ci >= 10:
                    esc = '7'
                else:
                    esc = 'Double Bogey'
    return esc

    
def get_results(players, course):
    player_map = read_player_data("players")
    lady_map = read_lady_data()
    auto_map = read_player_data("auto")
    courses_map =  read_course_data()
    lady_courses_map =  read_lady_course_file()

    course_tee,course_slope = courses_map[course]

    p_ci_80_a = []
    p_idx_map = {}

    result = []
    result.append([])
    
    for player in players:
        if player not in auto_map:
            ind = lookup_index(player_map[player])
        else:
            ind = float(auto_map[player])
        if player in lady_map:
            if course not in lady_courses_map:
                return None;
            lady_tee, lady_slope, lady_rate, man_rate = lady_courses_map[course]
            if float(lady_rate) > float(man_rate):
                lady_adj = int(float(lady_rate) - float(man_rate) + 0.5)
            else:
                lady_adj = int(float(lady_rate) - float(man_rate) - 0.5)
            slope = lady_slope
            lady_str = "Lady %s: adjust index %d -- tee(%s) with lady(%s/%s), man (%s/%s)" % (player, lady_adj, lady_tee, lady_rate, lady_slope, man_rate, course_slope)
            result[0].append(lady_str)
        else:
            slope = course_slope
            lady_adj = 0
        p_ci = int(ind * float(slope) / 113.0 + 0.5)
        p_ci_80 = int(p_ci * 0.8 + 0.5)
        p_idx_map[player] = (ind, p_ci, p_ci_80, lady_adj)
        p_ci_80_a.append(p_ci_80 + lady_adj)

    result.append([min(p_ci_80_a), course, course_tee, course_slope])
    result.append([])

    for player in players:
        ind, p_ci, p_ci_80, lady_adj = p_idx_map[player]
        result[2].append([player, player_map[player], ind, p_ci, p_ci_80, p_ci_80 + lady_adj - result[1][0], get_esc(p_ci)])

    return result
