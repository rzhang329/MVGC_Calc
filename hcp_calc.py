from mvgc_calculate import lookup_index

"""class HCPCalc:
    def __init__(self, player_ghin, course_tee):
        self.ghin = player_ghin
        self.tee = course_tee
        self.index = lookup_index(ghin)

    def get_personal_index(self):
        return self.index

    def get_course_index(self):
        return int(round(self.index * tee["Slope"] / 113.0 * 0.8))"""

def calculate_hcp(ghin, tee):
    p_index = lookup_index(ghin)
    c_index = int(round(p_index * tee["Slope"] / 113.0 * 0.8))
    return p_index, c_index
