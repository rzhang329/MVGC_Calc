import webapp2
from mvgc_calculate import get_results

mainFile = open("MainPage1.html")
MAIN_HTML_1 = mainFile.read()
mainFile.close()
mainFile = open("Players.html")
PLAYERS_HTML = mainFile.read()
mainFile.close()
mainFile = open("MainPage2.html")
MAIN_HTML_2 = mainFile.read()
mainFile.close()
mainFile = open("Courses.html")
COURSES_HTML = mainFile.read()
mainFile.close()
mainFile = open("MainPage3.html")
MAIN_HTML_3 = mainFile.read()
mainFile.close()

indexFile = open("Index1.html")
INDEX_HTML_1 = indexFile.read()
indexFile.close()
indexFile = open("Index2.html")
INDEX_HTML_2 = indexFile.read()
indexFile.close()

LADY_COURSE_ERROR = "Error. Female player selected, but no female handicap data for selected course. Please contact administrator for help."

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(MAIN_HTML_1)
        for i in range(0, 4):
            self.response.write(PLAYERS_HTML)
        self.response.write(MAIN_HTML_2)
        self.response.write(COURSES_HTML)
        self.response.write(MAIN_HTML_3)

class Index(webapp2.RequestHandler):
    def post(self):
        players = []
        for player in self.request.get_all("people"):
            if player != "none":
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
        self.response.write(INDEX_HTML_2)
        for info in data[2]:
            info_str = "<tr><td>%s</td><td>%s</td><td>%g</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td></tr>" % (info[0], info[1], info[2], info[3], info[4], info[5], info[6])
            self.response.write(info_str)
        self.response.write("</table></body></html>")
        
        
app = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/index", Index)], debug=True)
