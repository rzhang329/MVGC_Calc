from google.appengine.ext import ndb
from parse_text.py import Parser
import webapp2
import datetime

game_list = ndb.Key("MVGC_Data", "games")
gcourse_list = ndb.Key("MVGC_Data", "golf_courses")
player_list = ndb.Key("MVGC_Data", "players")
lady_list = ndb.Key("MVGC_Data", "ladies")

class Player(ndb.Model):
    name = ndb.StringProperty()
    ghin = ndb.StringProperty()

class Person(ndb.Model):
    name = ndb.StringProperty()
    male = ndb.BooleanProperty()
    p_index = ndb.FloatProperty()
    c_index = ndb.IntegerProperty()
    holes = ndb.StructuredProperty(Hole, repeated=True)
    cosign = ndb.StringProperty()

class Hole(ndb.Model):
    num = ndb.IntegerProperty()
    own_score = ndb.IntegerProperty()
    co_score = ndb.IntegerProperty()
    score = ndb.IntegerProperty()
    delta = ndb.IntegerProperty()

class Game(ndb.Model):
    name = ndb.StringProperty()
    player_list = ndb.StructuredProperty(Person, repeated=True)
    course = ndb.JsonProperty()
    men_tee = ndb.StringProperty()
    women_tee = ndb.StringProperty()
    date = ndb.DateProperty()
    board = ndb.JsonProperty()

class GCourse(ndb.Model):
    name = ndb.StringProperty()
    data = ndb.TextProperty()

def set_score(game, player, entry, score):
    entry.own_score = None
    entry.co_score = None
    net = score
    diff = "Men HCP"
    if not player.male:
        diff = "Women HCP"
    hole_data = game.course["Holes"][entry.num - 1]
    net -= player.c_index / 18 + (1 if hole_data[diff] < (player.c_index % 18) else 0)
    entry.score = net
    entry.delta = net - hole_data["Par"]

def input_score(match, name, hole, score, cosign):
    game = Game.query(ancestor=game_list).filter(Game.name=match).fetch()[0]
    player = filter(lambda x: x.name==name, game.player_list)[0]
    entry = Person.holes[hole - 1]
    if cosign:
        if entry.own_score is None:
            entry.co_score = score
        else:
            if entry.own_score == score:
                set_score(game, player, entry, score)
            else:
                return False
    else:
        if entry.co_score is None:
            entry.own_score = score
        else:
            if entry.co_score = score:
                set_score(game, player, entry, score)
            else:
                return False
    player.put()
    return True

def convert_leaders(course, entry):
    holes = 0
    total = 0
    par = 0
    for hole in entry.holes:
        if hole.score is not None:
            holes += 1
            total += hole.score
            delta += hole.delta
    return {"Name": entry.name, "Holes": holes, "Total": total, "Delta": delta}

def refresh_board(match):
    game = Game.query(ancestor=game_list).filter(Game.name=match).fetch()[0]
    board = map(lambda x: convert_leaders(game.course, x), game.player_list)
    board.sort(lambda x, y: x["Delta"] - y["Delta"])
    game.board = board

def start_game(game_name, course_name, year, month, day, men, women):
    course_entry = GCourse.query(ancestor=gcourse_list).filter(name=course_name).fetch()[0]
    course_data = Parser(course_entry.data).get_course()
    date_data = date(year, month, day)
    final_name = game_name
    if final_name == "":
        final_name = course_entry.name + " " + date_data.isoformat()
    game = Game(parent=game_list, name=final_name, course=course_data, men_tee=men, women_tee=women, date=date_data)
    game.put()

def init_holes(entry):
    entry.holes = []
    for index in range(1, 19):
        entry.holes.append(Hole(num=index))

def enter_player(game_name, player_name):
    game = Game.query(ancestor=game_list).filter(name=game_name).fetch()[0]
    player = Player.query(ancestor=player_list).filter(name=player_name).fetch()[0]
    check_female = Player.query(ancestor=lady_list).filter(name=player_name).fetch()
    tee = ""
    is_male = True
    if check_female == []:
        tee = game.men_tee
    else:
        tee = game.women_tee
        is_male = False
    calc = HCPCalc(player.ghin, game.course["Tees"][tee])
    p_ind = calc.get_personal_index()
    c_ind = calc.get_course_index()
    entry = Person(name=player_name, male=is_male, p_index = p_ind, c_index = c_ind)
    init_holes(entry)
    if game.player_list is None:
        game.player_list = []
    game.player_list.append(entry)
    game.put()

def get_player_info(game_name, player_name):
    game = Game.query(ancestor=game_list).filter(name=game_name).fetch()[0]
    player = filter(lambda x: x.name=player_name, game.player_list)[0]
    result = {"Name": player.name, "Personal Index": player.p_index, "Course Index": player.c_index, "Holes": []}
    for hole in player.holes:
        data = {}
        data["Score"] = hole.score
        data["Delta"] = hole.delta
        result["Holes"].append(data)
    result["Rank"] = [x for x, y in enumerate(game.board) if y["Name"]==player_name][0] + 1
    return result

def enter_cosign(game_name, player_name, cosign_name):
    game = Game.query(ancestor=game_list).filter(name=game_name).fetch()[0]
    player = filter(lambda x: x.name==player_name, game.player_list)[0]
    player.cosign = cosign_name

class GameServer(webapp2.RequestHandler):
    def post(self):
