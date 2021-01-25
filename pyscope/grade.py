class GSGrade():

    def __init__(self, student_name, assign_name, aid, points, score, url):
        '''Create a assignment object'''
        self.student_name = student_name
        self.assign_name = assign_name
        self.aid = str(aid)
        self.points = str(points)
        self.score = str(score)
        self.url = url
        
    def __str__(self):
        return '[#Grade# ' + self.student_name + ' - ' + self.assign_name + ' (' + self.aid + ') ' + self.score + '/' + self.points + ']'
