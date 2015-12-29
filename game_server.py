from google.appengine.ext import ndb
from parse_text import Parser
from hcp_calc import calculate_hcp
import webapp2
import datetime
import json

game_list = ndb.Key("MVGC_Data", "games")
gcourse_list = ndb.Key("MVGC_Data", "golf_courses")
people_list = ndb.Key("MVGC_Data", "people")
player_list = ndb.Key("MVGC_Data", "players")
lady_list = ndb.Key("MVGC_Data", "ladies")

class Player(ndb.Model):
    name = ndb.StringProperty()
    ghin = ndb.StringProperty()

class Person(ndb.Model):
    name = ndb.StringProperty()
    ghin = ndb.StringProperty()
    male = ndb.BooleanProperty()

class GPlayer(ndb.Model):
    name = ndb.StringProperty()
    male = ndb.BooleanProperty()
    p_index = ndb.FloatProperty()
    c_index = ndb.IntegerProperty()
    cosign = ndb.StringProperty()
    holes = ndb.KeyProperty()

class Hole(ndb.Model):
    num = ndb.IntegerProperty()
    own_score = ndb.IntegerProperty()
    co_score = ndb.IntegerProperty()
    score = ndb.IntegerProperty()
    delta = ndb.IntegerProperty()

class Game(ndb.Model):
    name = ndb.StringProperty()
    course = ndb.JsonProperty()
    men_tee = ndb.StringProperty()
    women_tee = ndb.StringProperty()
    date = ndb.DateProperty()
    players = ndb.KeyProperty()

class GCourse(ndb.Model):
    name = ndb.StringProperty()
    data = ndb.JsonProperty()

def create_person(person_name, person_ghin, person_male):
    person = Person(parent=people_list, name=person_name, ghin=person_ghin, male=person_male)
    person.put()

def get_person(person_name):
    person = Person.query(ancestor=people_list).filter(Person.name==person_name).fetch()[0]
    result = {}
    result["Name"] = person.name
    result["Ghin"] = person.ghin
    result["Male"] = person.male
    return result

def delete_person(person_name):
    person = Person.query(ancestor=people_list).filter(Person.name==person_name).fetch()[0]
    person.key.delete()

def set_score(game, player, entry, score):
    entry.own_score = None
    entry.co_score = None
    net = score
    diff = "Men HCP"
    if not player.male:
        diff = "Women HCP"
    hole_diff = game.course["Holes"][diff][entry.num - 1]
    net -= player.c_index / 18 + (1 if hole_diff < (player.c_index % 18) else 0)
    entry.score = net
    entry.delta = net - game.course["Holes"]["Par"][entry.num - 1]
    entry.put()

def modify_score(game_name, player_name, input_name, hole, score):
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    player = GPlayer.query(ancestor=game.players).filter(GPlayer.name==player_name).fetch()[0]
    entry_list = Hole.query(ancestor=player.holes).filter(Hole.num==hole).fetch()
    entry = entry_list[0] if len(entry_list) > 0 else Hole(parent=player.holes, num=hole)
    result = "Error. You are not registered as this player's cosigner"
    if input_name == player.name:
        if entry.co_score is None:
            entry.own_score = score
            entry.put()
            result = "Score recorded."
        else:
            if entry.co_score == score:
                set_score(game, player, entry, score)
                result = "Score recorded and finalized."
            else:
                result = "Error. Score mismatch. Please check with cosigner."
    elif player.cosign is None:
        result = "Error. Player does not have a cosigner."
    elif input_name == player.cosign:
        if entry.own_score is None:
            entry.co_score = score
            entry.put()
            result = "Score recorded."
        else:
            if entry.own_score == score:
                set_score(game, player, entry, score)
                result = "Score recorded and finalized."
            else:
                result = "Error. Score mismatch. Please check with player."
    return result

def get_summary(player):
    result = {"Name": player.name, "Holes": 0, "Total": 0, "Delta": 0}
    holes = Hole.query(ancestor=player.holes).fetch()
    for hole in holes:
        if hole.score is not None:
            result["Holes"] += 1
            result["Total"] += hole.score
            result["Delta"] += hole.delta
    return result

def get_board(game_name):
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    players = GPlayer.query(ancestor=game.players).fetch()
    board = map(get_summary, players)
    board.sort(lambda x, y: x["Delta"] - y["Delta"])
    return board

def create_game(game_name, course_name, year, month, day, men, women):
    course_entry = GCourse.query(ancestor=gcourse_list).filter(GCourse.name==course_name).fetch()[0]
    date_data = datetime.date(year, month, day)
    final_name = game_name
    if final_name == "":
        final_name = course_entry.name + " " + date_data.isoformat()
    game = Game(parent=game_list, name=final_name, course=course_entry.data, men_tee=men, women_tee=women, date=date_data)
    game.players = ndb.Key("MVGC_Data", "game_%s" % final_name)
    game.put()

def create_player(game_name, player_name):
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    person = Person.query(ancestor=people_list).filter(Person.name==player_name).fetch()[0]
    tee = game.men_tee
    box = "Men"
    if not person.male:
        tee = game.women_tee
        box = "Women"
    p_ind, c_ind = calculate_hcp(person.ghin, game.course["Tees"][tee][box])
    player = GPlayer(parent=game.players, name=player_name, male=person.male, p_index = p_ind, c_index = c_ind)
    player.holes = ndb.Key("MVGC_Data", "player_%s" % player_name)
    player.put()

def create_guest(game_name, player_name, player_ghin, player_male):
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    tee = game.men_tee
    box = "Men"
    if not player_male:
        tee = game.women_tee
        box = "Women"
    p_ind, c_ind = calculate_hcp(player_ghin, game.course["Tees"][tee][box])
    player = GPlayer(parent=game.players, name=player_name, male=player_male, p_index = p_ind, c_index = c_ind)
    player.holes = ndb.Key("MVGC_Data", "player_%s" % player_name)
    player.put()

def get_player(game_name, player_name):
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    player = GPlayer.query(ancestor=game.players).filter(GPlayer.name==player_name).fetch()[0]
    result = {"Name": player.name, "Personal Index": player.p_index, "Course Index": player.c_index, "Holes": []}
    for index in range(18):
        result["Holes"].append({"Score": "-", "Delta": "-"})
    holes = Hole.query(ancestor=player.holes).fetch()
    for hole in holes:
        if hole.score is not None:
            result["Holes"][hole.num - 1]["Score"] = hole.score
            result["Holes"][hole.num - 1]["Delta"] = hole.delta
    #result["Rank"] = [x for x, y in enumerate(game.board) if y["Name"]==player_name][0] + 1
    result["Cosign"] = player.cosign
    return result

def delete_player(game_name, player_name):
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    player = GPlayer.query(ancestor=game.players).filter(GPlayer.name==player_name).fetch()[0]
    player.key.delete()

def create_cosign(game_name, player_name, cosign_name):
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    player = GPlayer.query(ancestor=game.players).filter(GPlayer.name==player_name).fetch()[0]
    player.cosign = cosign_name
    player.put()
    return "Cosigner registered."

def create_course(course_name, raw_data):
    course_data = Parser(course_name, raw_data).get_course()
    course = GCourse(parent=gcourse_list, name=course_name, data=course_data)
    course.put()

def get_course(course_name):
    course = GCourse.query(ancestor=gcourse_list).filter(GCourse.name==course_name).fetch()[0]
    return course.data

def delete_game(game_name):
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    players = GPlayer.query(ancestor=game.players).fetch()
    for player in players:
        holes = Hole.query(ancestor=player.holes)
        for hole in holes:
            hole.key.delete()
        player.delete()
    game.delete()

def get_game(game_name):
    result = {}
    game = Game.query(ancestor=game_list).filter(Game.name==game_name).fetch()[0]
    result["Name"] = game.name
    result["Course"] = game.course["Name"]
    result["Date"] = game.date.isoformat()
    return result

def get_tees(course_name):
    course = GCourse.query(ancestor=gcourse_list).filter(GCourse.name==course_name).fetch()[0]
    data = course.data["Tees"].keys()
    result = {}
    result["Men"] = filter(lambda x: "Men" in course.data["Tees"][x], data)
    result["Women"] = filter(lambda x: "Women" in course.data["Tees"][x], data)
    return result

def get_game_list():
    games = Game.query(ancestor=game_list).fetch()
    result = []
    for game in games:
        info = {}
        info["Name"] = game.name
        info["Course"] = game.course["Name"]
        info["Date"] = game.date.isoformat()
        result.append(info)
    return result

def copy_people():
    old_list = Player.query(ancestor=player_list).fetch()
    for player in old_list:
        person = Person(parent=people_list, name=player.name, ghin=player.ghin, male=True)
        person.put()
    l_list = Player.query(ancestor=lady_list).fetch()
    for player in l_list:
        person = Person.query(ancestor=people_list).filter(Person.name==player.name).fetch()[0]
        person.male = False
        person.put()

def list_people():
    people = Person.query(ancestor=people_list).fetch()
    return map(lambda x: x.name, people)

class GameServer(webapp2.RequestHandler):
    def post(self):
        req = self.request.get("request")
        if req == "create_person":
            person = self.request.get("person_name")
            ghin = self.request.get("person_ghin")
            male = self.request.get("person_male")
            create_person(person, ghin, male=="True")
        elif req == "get_person":
            person = self.request.get("person_name")
            self.response.write(json.dumps(get_person(person)))
        elif req == "delete_person":
            person = self.request.get("person_name")
            delete_person(person)
        elif req == "create_game":
            game = self.request.get("game_name")
            course = self.request.get("course_name")
            men_tee = self.request.get("men_tee")
            women_tee = self.request.get("women_tee")
            year = int(self.request.get("year"))
            month = int(self.request.get("month"))
            day = int(self.request.get("day"))
            create_game(game, course, year, month, day, men_tee, women_tee)
        elif req == "get_game":
            game = self.request.get("game_name")
            self.response.write(json.dumps(get_game(game)))
        elif req == "delete_game":
            game = self.request.get("game_name")
            delete_game(game)
        elif req == "get_tees":
            course = self.request.get("course_name")
            self.response.write(json.dumps(get_tees(course)))
        elif req == "create_course":
            course_name = self.request.get("course_name")
            course_data = self.request.get("course_data")
            create_course(course_name, course_data)
            self.response.write("Course uploaded.")
        elif req == "get_course":
            course_name = self.request.get("course_name")
            self.response.write(json.dumps(get_course(course_name)))
        elif req == "create_player":
            game = self.request.get("game_name")
            player = self.request.get("player_name")
            create_player(game, player)
        elif req == "create_guest":
            game = self.request.get("game_name")
            name = self.request.get("guest_name")
            ghin = self.request.get("guest_ghin")
            male = self.request.get("guest_male")
            create_guest(game, name, ghin, male=="True")
        elif req == "get_player":
            game = self.request.get("game_name")
            player = self.request.get("player_name")
            self.response.write(json.dumps(get_player(game, player)))
        elif req == "delete_player":
            game = self.request.get("game_name")
            player = self.request.get("player_name")
            delete_player(game, player)
        elif req == "get_board":
            game = self.request.get("game_name")
            self.response.write(json.dumps(get_board(game)))
        elif req == "get_game_list":
            self.response.write(json.dumps(get_game_list()))
        elif req == "create_cosign":
            game = self.request.get("game_name")
            player = self.request.get("player_name")
            cosign = self.request.get("cosign_name")
            self.response.write(create_cosign(game, player, cosign))
        elif req == "modify_score_own":
            game = self.request.get("game_name")
            player = self.request.get("player_name")
            hole = int(self.request.get("hole_num"))
            score = int(self.request.get("score"))
            self.response.write(modify_score(game, player, player, hole, score))
        elif req == "modify_score_cosign":
            game = self.request.get("game_name")
            player = self.request.get("player_name")
            cosign = self.request.get("cosign_name")
            hole = int(self.request.get("hole_num"))
            score = int(self.request.get("score"))
            self.response.write(modify_score(game, player, cosign, hole, score))
        else:
            self.response.write("Invalid request.")
