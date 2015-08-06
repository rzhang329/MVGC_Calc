#!/usr/bin/python

import os,re
import BeautifulSoup
import urllib

def read_player_file(filename):
    dd = {}
    for line in open(filename, 'r').read().splitlines():
        ghin,name = line.split("\t")
        name = ''.join(name.split('\"'))
        dd[name] = ghin
    return dd

def read_course_file(filename):
    dd = {}
    for line in open(filename, 'r').read().splitlines():
        name,tee,slope = line.split("\t")
        dd[name] = (tee,slope)
    return dd

def read_lady_course_file(filename):
    dd = {}
    for line in open(filename, 'r').read().splitlines():
        name,tee,slope,lady_rate,man_rate = line.split("\t")
        dd[name] = (tee,slope,lady_rate,man_rate)
    return dd

def read_lady_player_file(filename):
    dd = set()
    for name in open(filename, 'r').read().splitlines():
      dd.add(name)
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
    players_ghin_map = read_player_file("mvgc_player_ghin.txt")
    players_idx_map = read_player_file("mvgc_player_index.txt")
    courses_map =  read_course_file("mvgc_course_index.txt")

    lady_courses_map =  read_lady_course_file("mvgc_course_lady_index.txt")
    lady_players = read_lady_player_file("mvgc_lady_player.txt")

    course_tee,course_slope = courses_map[course]

    p_ci_80_a = []
    p_idx_map = {}

    result = []
    result.append([])
    
    for player in players:
        if player not in players_idx_map:
          ind = lookup_index(players_ghin_map[player])
        else:
          ind = float(players_idx_map[player])
        if player in lady_players:
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
        result[2].append([player, players_ghin_map[player], ind, p_ci, p_ci_80, p_ci_80 + lady_adj - result[1][0], get_esc(p_ci)])

    return result
