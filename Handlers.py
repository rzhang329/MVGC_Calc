import webapp2
from google.appengine.ext import ndb
from mvgc_calculate import get_results

mainFile = open("MainPage.html")
MAIN_HTML = mainFile.read()
mainFile.close()
mainFile = open("MainPage1.html")
MAIN_HTML_1 = mainFile.read()
mainFile.close()
mainFile = open("MainPage2.html")
MAIN_HTML_2 = mainFile.read()
mainFile.close()
mainFile = open("MainPage3.html")
MAIN_HTML_3 = mainFile.read()
mainFile.close()

androidFile = open("DownloadPage.html")
ANDROID_HTML = androidFile.read()
androidFile.close()

indexFile = open("Index1.html")
INDEX_HTML_1 = indexFile.read()
indexFile.close()
indexFile = open("Index2.html")
INDEX_HTML_2 = indexFile.read()
indexFile.close()

LADY_COURSE_ERROR = "Error. Female player selected, but no female handicap data for selected course. Please contact administrator for help."

password = "mvgcmodify"

player_list = ndb.Key("MVGC_Data", "players")
course_list = ndb.Key("MVGC_Data", "courses")
lady_list = ndb.Key("MVGC_Data", "ladies")
auto_list = ndb.Key("MVGC_Data", "auto")
lcourse_list = ndb.Key("MVGC_Data", "lady_courses")

mod_form = '<br><form action="%s" method="post">Password: <input type="password" name="password"><br><input type="submit" value="%s"></form><br>'
player_form = '<br>Name<br><input type="text" name="%s"><br>GHIN<br><input type="text" name="%s">'
auto_form = '<br>Name<br><input type="text" name="%s"><br>Auto Index<br><input type="text" name="%s">'
hidden_form = '<input type="hidden" name="password" value="%s">' % password
lady_form = '<br>Name<br><input type="text" name="%s">'
course_form = '<br>Course<br><input type="text" name="%s"><br>Tee Box<br><input type="text" name="%s"><br>Slope<br><input type="text" name="%s"><br>'
lcourse_form = '<br>Course<br><input type="text" name="%s"><br>Tee Box<br><input type="text" name="%s"><br>Slope<br><input type="text" name="%s"><br><br>Lady Rate<br><input type="text" name="%s"><br><br>Man Rate<br><input type="text" name="%s"><br>'
end_form = '<br><br><input type="submit" value="Submit"></form></body></html>'

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

def createSelect(data_list, select_name):
    sort_list = []
    result = []
    result.append('<select name="%s">\n' % select_name)
    result.append('<option value=""></option>\n')
    for item in data_list:
        result.append('<option value="%s">%s</option>\n' % (item.name, item.name))
    result.append('</select>')
    return ''.join(result)

class AndroidApp(webapp2.RequestHandler):
    def get(self):
        self.response.write(ANDROID_HTML)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.display(4)

    def post(self):
        num = int(self.request.get("num_players"))
        if 0 < num < 100:
            self.display(num)
        else:
            self.response.write("Please enter a number between 0 and 100")

    def display(self, num_players):
        data_list = Player.query(ancestor=player_list).fetch()
        data_list.sort(key=lambda x:x.name)
        data = "<br>%s<br>" % createSelect(data_list, "people")
        self.response.write(MAIN_HTML_1)
        for i in range(0, num_players):
            self.response.write(data)
        self.response.write(MAIN_HTML_2)
        data_list = Course.query(ancestor=course_list).fetch()
        data_list.sort(key=lambda x:x.name)
        data = "<br>%s<br>" % createSelect(data_list, "places")
        self.response.write(data)
        self.response.write(MAIN_HTML_3)

class Index(webapp2.RequestHandler):
    def post(self):
        players = []
        for player in self.request.get_all("people"):
            if player != "":
                players.append(player)
        course = self.request.get("places")
        data = get_results(players, course)
        if data is None:
            self.response.write(LADY_COURSE_ERROR)
            return
        course_str = "Golf Course: %s<br> Tee Box: %s<br>Slope: %s<br>" % (data[1][1], data[1][2], data[1][3])
        lowest_str = "<br>The lowest course index is %d<br><br>" % data[1][0]
        self.response.write(INDEX_HTML_1)
        self.response.write(course_str)
        self.response.write(lowest_str)
        for lady_str in data[0]:
            self.response.write(lady_str + "<br>")
        self.response.write("<br>")
        text_data = []
        text_data.append("<pre>")
        text_data.append("{:<20} \t{:<13} \t{:<13} \t{:<13} \t{:<13}".format('', 'Personal', 'Course', '80% Course', 'Index'))
        text_data.append("\n")
        text_data.append("{:<20} \t{:<13} \t{:<13} \t{:<13} \t{:<13} \t{:<4}".format('Player', 'Index', 'Index', 'Index', 'Allowance', 'ESC'))
        text_data.append("\n")
        for info in data[2]:
            text_data.append("{:<20} \t{:<13.1f} \t{:<13d} \t{:<13d} \t{:<13d} \t{:<4}".format(info[0], info[2], info[3], info[4], info[5], info[6]))
            text_data.append("\n")
        text_data.append("</pre>")
        self.response.write(''.join(text_data))
        self.response.write(INDEX_HTML_2)
        for info in data[2]:
            info_str = "<tr><td>%s</td><td>%g</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td></tr>" % (info[0], info[2], info[3], info[4], info[5], info[6])
            self.response.write(info_str)
        self.response.write("</table></body></html>")

class Modify(webapp2.RequestHandler):
    def get(self):
        self.response.write("<html><body>")
        self.response.write(mod_form % ("/mod_players", "Players"))
        self.response.write(mod_form % ("/mod_courses", "Courses"))
        self.response.write(mod_form % ("/mod_ladies", "Lady players"))
        self.response.write(mod_form % ("/mod_auto", "Automatic indexes"))
        self.response.write(mod_form % ("/mod_lcourses", "Lady courses"))
        self.response.write("</body></html>")

class ModifyPlayers(webapp2.RequestHandler):
    def show_data(self):
        self.response.write("<html><body><table border='1' cellpadding='5'>")
        self.response.write("<tr><th>Name</th><th>GHIN</th></tr>")
        p_list = Player.query(ancestor=player_list).fetch()
        p_list.sort(key=lambda x: x.name)
        for player in p_list:
            self.response.write("<tr><td>%s</td><td>%s</td></tr>" % (player.name, player.ghin))
        self.response.write("</table><br><strong>Add entry</strong><br>")
        self.response.write('<form action="/mod_players" method="post">')
        self.response.write(player_form % ("add_name", "add_ghin"))
        self.response.write("<br><strong>Modify entry</strong><br>")
        self.response.write(createSelect(p_list, "modify"))
        self.response.write(player_form % ("mod_name", "mod_ghin"))
        self.response.write("<br><br><strong>Delete entry</strong><br>")
        self.response.write(createSelect(p_list, "delete"))
        self.response.write(hidden_form)
        self.response.write(end_form)

    def post(self):
        if self.request.get("password") == password:
            add_name = self.request.get("add_name")
            add_ghin = self.request.get("add_ghin")
            p_mod = self.request.get("modify")
            p_del = self.request.get("delete")
            if add_name != "" and add_ghin != "":
                entry = Player(parent=player_list, name=add_name, ghin=add_ghin)
                entry.put()
            if p_mod != "":
                entry = Player.query(ancestor=player_list).filter(Player.name == p_mod).fetch()[0]
                mod_name = self.request.get("mod_name")
                mod_ghin = self.request.get("mod_ghin")
                if mod_name != "":
                    entry.name = mod_name
                if mod_ghin != "":
                    entry.ghin = mod_ghin
                entry.put()
            if p_del != "":
                Player.query(ancestor=player_list).filter(Player.name == p_del).fetch()[0].key.delete()
            self.show_data()
        else:
            self.response.write("Incorrect password.")

class ModifyCourses(webapp2.RequestHandler):
    def show_data(self):
        self.response.write("<html><body><table border='1' cellpadding='5'>")
        self.response.write("<tr><th>Course</th><th>Tee Box</th><th>Slope</th></tr>")
        c_list = Course.query(ancestor=course_list).fetch()
        c_list.sort(key=lambda x: x.name)
        for item in c_list:
            self.response.write("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (item.name, item.tee, item.slope))
        self.response.write("</table><br><strong>Add entry</strong><br>")
        self.response.write('<form action="/mod_courses" method="post">')
        self.response.write(course_form % ("add_name", "add_tee", "add_slope"))
        self.response.write("<br><strong>Modify entry</strong><br>")
        self.response.write(createSelect(c_list, "modify"))
        self.response.write(course_form % ("mod_name", "mod_tee", "mod_slope"))
        self.response.write("<br><br><strong>Delete entry</strong><br>")
        self.response.write(createSelect(c_list, "delete"))
        self.response.write(hidden_form)
        self.response.write(end_form)
        
    def post(self):
        if self.request.get("password") == password:
            add_name = self.request.get("add_name")
            add_tee = self.request.get("add_tee")
            add_slope = self.request.get("add_slope")
            c_mod = self.request.get("modify")
            c_del = self.request.get("delete")
            if add_name != "" and add_tee != "" and add_slope != "":
                entry = Course(parent=course_list, name=add_name, tee=add_tee, slope=add_slope)
                entry.put()
            if c_mod != "":
                entry = Course.query(ancestor=course_list).filter(Course.name == c_mod).fetch()[0]
                mod_name = self.request.get("mod_name")
                mod_tee = self.request.get("mod_tee")
                mod_slope = self.request.get("mod_slope")
                if mod_name != "":
                    entry.name = mod_name
                if mod_tee != "":
                    entry.tee = mod_tee
                if mod_slope != "":
                    entry.slope = mod_slope
                entry.put()
            if c_del != "":
                Course.query(ancestor=course_list).filter(Course.name == c_del).fetch()[0].key.delete()
            self.show_data()
        else:
            self.response.write("Incorrect password.")

class ModifyLadies(webapp2.RequestHandler):
    def show_data(self):
        self.response.write("<html><body><table border='1' cellpadding='5'>")
        self.response.write("<tr><th>Name</th></tr>")
        p_list = Player.query(ancestor=lady_list).fetch()
        p_list.sort(key=lambda x: x.name)
        for player in p_list:
            self.response.write("<tr><td>%s</td></tr>" % player.name)
        self.response.write("</table><br><strong>Add entry</strong><br>")
        self.response.write('<form action="/mod_ladies" method="post">')
        self.response.write(lady_form % "add_name")
        self.response.write("<br><strong>Modify entry</strong><br>")
        self.response.write(createSelect(p_list, "modify"))
        self.response.write(lady_form % "mod_name")
        self.response.write("<br><br><strong>Delete entry</strong><br>")
        self.response.write(createSelect(p_list, "delete"))
        self.response.write(hidden_form)
        self.response.write(end_form)

    def post(self):
        if self.request.get("password") == password:
            add_name = self.request.get("add_name")
            p_mod = self.request.get("modify")
            p_del = self.request.get("delete")
            if add_name != "":
                entry = Player(parent=lady_list, name=add_name, ghin="")
                entry.put()
            if p_mod != "":
                entry = Player.query(ancestor=lady_list).filter(Player.name == p_mod).fetch()[0]
                mod_name = self.request.get("mod_name")
                if mod_name != "":
                    entry.name = mod_name
                    entry.put()
            if p_del != "":
                Player.query(ancestor=lady_list).filter(Player.name == p_del).fetch()[0].key.delete()
            self.show_data()
        else:
            self.response.write("Incorrect password.")

class ModifyAuto(webapp2.RequestHandler):
    def show_data(self):
        self.response.write("<html><body><table border='1' cellpadding='5'>")
        self.response.write("<tr><th>Name</th><th>Auto Index</th></tr>")
        p_list = Player.query(ancestor=auto_list).fetch()
        p_list.sort(key=lambda x: x.name)
        for player in p_list:
            self.response.write("<tr><td>%s</td><td>%s</td></tr>" % (player.name, player.ghin))
        self.response.write("</table><br><strong>Add entry</strong><br>")
        self.response.write('<form action="/mod_auto" method="post">')
        self.response.write(auto_form % ("add_name", "add_ghin"))
        self.response.write("<br><strong>Modify entry</strong><br>")
        self.response.write(createSelect(p_list, "modify"))
        self.response.write(auto_form % ("mod_name", "mod_ghin"))
        self.response.write("<br><br><strong>Delete entry</strong><br>")
        self.response.write(createSelect(p_list, "delete"))
        self.response.write(hidden_form)
        self.response.write(end_form)
    
    def post(self):
        if self.request.get("password") == password:
            add_name = self.request.get("add_name")
            add_ghin = self.request.get("add_ghin")
            p_mod = self.request.get("modify")
            p_del = self.request.get("delete")
            if add_name != "" and add_ghin != "":
                entry = Player(parent=auto_list, name=add_name, ghin=add_ghin)
                entry.put()
            if p_mod != "":
                entry = Player.query(ancestor=auto_list).filter(Player.name == p_mod).fetch()[0]
                mod_name = self.request.get("mod_name")
                mod_ghin = self.request.get("mod_ghin")
                if mod_name != "":
                    entry.name = mod_name
                if mod_ghin != "":
                    entry.ghin = mod_ghin
                entry.put()
            if p_del != "":
                Player.query(ancestor=auto_list).filter(Player.name == p_del).fetch()[0].key.delete()
            self.show_data()
        else:
            self.response.write("Incorrect password.")

class ModifyLCourses(webapp2.RequestHandler):
    def show_data(self):
        self.response.write("<html><body><table border='1' cellpadding='5'>")
        self.response.write("<tr><th>Course</th><th>Tee Box</th><th>Slope</th><th>Lady Rate</th><th>Man Rate</th></tr>")
        c_list = LCourse.query(ancestor=lcourse_list).fetch()
        c_list.sort(key=lambda x: x.name)
        for item in c_list:
            self.response.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (item.name, item.tee, item.slope, item.lady_rate, item.man_rate))
        self.response.write("</table><br><strong>Add entry</strong><br>")
        self.response.write('<form action="/mod_lcourses" method="post">')
        self.response.write(lcourse_form % ("add_name", "add_tee", "add_slope", "add_lrate", "add_mrate"))
        self.response.write("<br><strong>Modify entry</strong><br>")
        self.response.write(createSelect(c_list, "modify"))
        self.response.write(lcourse_form % ("mod_name", "mod_tee", "mod_slope", "mod_lrate", "mod_mrate"))
        self.response.write("<br><br><strong>Delete entry</strong><br>")
        self.response.write(createSelect(c_list, "delete"))
        self.response.write(hidden_form)
        self.response.write(end_form)
    
    def post(self):
        if self.request.get("password") == password:
            add_name = self.request.get("add_name")
            add_tee = self.request.get("add_tee")
            add_slope = self.request.get("add_slope")
            add_lrate = self.request.get("add_lrate")
            add_mrate = self.request.get("add_mrate")
            c_mod = self.request.get("modify")
            c_del = self.request.get("delete")
            if add_name != "" and add_tee != "" and add_slope != "" and add_mrate != "" and add_lrate != "":
                entry = LCourse(parent=lcourse_list, name=add_name, tee=add_tee, slope=add_slope, lady_rate=add_lrate, man_rate=add_mrate)
                entry.put()
            if c_mod != "":
                entry = LCourse.query(ancestor=lcourse_list).filter(Course.name == c_mod).fetch()[0]
                mod_name = self.request.get("mod_name")
                mod_tee = self.request.get("mod_tee")
                mod_slope = self.request.get("mod_slope")
                mod_lrate = self.request.get("mod_lrate")
                mod_mrate = self.request.get("mod_mrate")
                if mod_name != "":
                    entry.name = mod_name
                if mod_tee != "":
                    entry.tee = mod_tee
                if mod_slope != "":
                    entry.slope = mod_slope
                if mod_lrate != "":
                    entry.lady_rate = mod_lrate
                if mod_mrate != "":
                    entry.man_rate = mod_mrate
                entry.put()
            if c_del != "":
                LCourse.query(ancestor=lcourse_list).filter(Course.name == c_del).fetch()[0].key.delete()
            self.show_data()
        else:
            self.response.write("Incorrect password.")

class MobileData(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        players = Player.query(ancestor=player_list).fetch()
        players.sort(key=lambda x: x.name)
        courses = Course.query(ancestor=course_list).fetch()
        courses.sort(key=lambda x: x.name)
        data = []
        for player in players:
            data.append("%s\n" % player.name)
        data.append(":")
        for course in courses:
            data.append("%s\n" % course.name)
        self.response.write(''.join(data))

class MobileResults(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = "text/plain"
        players = self.request.get_all("players")
        course = self.request.get("course")
        data = get_results(players, course)
        if data is None:
            self.response.write("0")
            return
        result = []
        result.append("1;")
        for info in data[0]:
            result.append("%s\n" % info)
        result.append(";")
        result.append("%d:%s:%s:%s;" % (data[1][0], data[1][1], data[1][2], data[1][3]))
        for info in data[2]:
            result.append("%s:%g:%d\n" % (info[0], info[2], info[5]))
        self.response.write(''.join(result))

app = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/mod", Modify),
    ("/mod_players", ModifyPlayers),
    ("/mod_courses", ModifyCourses),
    ("/mod_ladies", ModifyLadies),
    ("/mod_auto", ModifyAuto),
    ("/mod_lcourses", ModifyLCourses),
    ("/mobile_data", MobileData),
    ("/mobile_res", MobileResults),
    ("/androidapp", AndroidApp),
    ("/index", Index)], debug=False)
