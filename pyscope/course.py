import json, time
from enum import Enum
from bs4 import BeautifulSoup
try:
   from person import GSPerson
   from person import GSRole
except ModuleNotFoundError:
   from .person import GSPerson
   from .person import GSRole
try:
   from assignment import GSAssignment
except ModuleNotFoundError:
   from .assignment import GSAssignment
try:
   from grade import GSGrade
except ModuleNotFoundError:
   from .grade import GSGrade

class LoadedCapabilities(Enum):
    ASSIGNMENTS = 0
    ROSTER = 1
    GRADES = 2

class GSCourse():

    def __init__(self, cid, name, shortname, year, session):
        '''Create a course object that has lazy eval'd assignments'''
        self.cid = cid
        self.name = name
        self.shortname = shortname
        self.year = year
        self.session = session
        self.assignments = {}
        self.roster = {} # TODO: Maybe shouldn't dict. 
        self.grades = {}
        self.state = set() # Set of already loaded entitites (TODO what is the pythonic way to do this?)

    def __str__(self):
        return '[#Course# ' + self.shortname + ' (' + self.cid + ') ' + self.name + ']'

    def get_grades(self):
        '''
        Returns a CSV file of the gradebook
        '''
        # Handles CSV headers
        ret = 'username'
        for _, assignment in self.assignments.items():
            ret += ',' + assignment.name
        ret += '\n'
        # Handles each student's grades
        for pindex, person in self.roster.items():
            # Check if we are looking at a student or professor. TODO: Do professors have grades in gradescope?
            if GSRole.to_str(person.role) != 'Student':
                continue
            ret += person.email
            for _, grade in self.grades[pindex].items(): # TODO: need to ensure order of assignments is globally the same
                ret += ',' + grade.score
            ret += '\n'
        return ret

    # ~~~~~~~~~~~~~~~~~~~~~~PEOPLE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def add_person(self, name, email, role, sid = None, notify = False):
        self._check_capabilities({LoadedCapabilities.ROSTER})
        
        membership_resp = self.session.get('https://www.gradescope.com/courses/' + self.cid + '/memberships')
        parsed_membership_resp = BeautifulSoup(membership_resp.text, 'html.parser')

        authenticity_token = parsed_membership_resp.find('meta', attrs = {'name': 'csrf-token'} ).get('content')
        person_params = {
            "utf8": "✓",
            "user[name]" : name,
            "user[email]" : email,
            "user[sid]" : "" if sid is None else sid, 
            "course_membership[role]" : role.value,
            "button" : ""
        }
        if notify:
            person_params['notify_by_email'] = 1
        # Seriously. Why is this website so inconsistent as to where the csrf token goes?????????
        add_resp = self.session.post('https://www.gradescope.com/courses/' + self.cid + '/memberships',
                                     data = person_params,
                                     headers = {'x-csrf-token': authenticity_token})

        # TODO this is highly wasteful, need to likely improve this. 
        self.roster = {}
        self._lazy_load_roster()

    def remove_person(self, name):
        self._check_capabilities({LoadedCapabilities.ROSTER})
        
        membership_resp = self.session.get('https://www.gradescope.com/courses/' + self.cid + '/memberships')
        parsed_membership_resp = BeautifulSoup(membership_resp.text, 'html.parser')

        authenticity_token = parsed_membership_resp.find('meta', attrs = {'name': 'csrf-token'} ).get('content')
        remove_params = {
            "_method" : "delete",
            "authenticity_token" : authenticity_token
        }
        remove_resp = self.session.post('https://www.gradescope.com/courses/'+self.cid+'/memberships/'
                                     +self.roster[name].data_id,
                                     data = remove_params,
                                     headers = {'x-csrf-token': authenticity_token})

        # TODO this is highly wasteful, need to likely improve this. 
        self.roster = {}
        self._lazy_load_roster()

    def change_person_role(self, name, role):
        self._check_capabilities({LoadedCapabilities.ROSTER})
        
        membership_resp = self.session.get('https://www.gradescope.com/courses/' + self.cid + '/memberships')
        parsed_membership_resp = BeautifulSoup(membership_resp.text, 'html.parser')

        authenticity_token = parsed_membership_resp.find('meta', attrs = {'name': 'csrf-token'} ).get('content')
        role_params = {
            "course_membership[role]" : role.value,
        }
        role_resp = self.session.patch('https://www.gradescope.com/courses/'+self.cid+'/memberships/'
                                     +self.roster[name].data_id+'/update_role' ,
                                     data = role_params,
                                     headers = {'x-csrf-token': authenticity_token})

        # TODO this is highly wasteful, need to likely improve this. 
        self.roster = {}
        self._lazy_load_roster()

    # ~~~~~~~~~~~~~~~~~~~~~~ASSIGNMENTS~~~~~~~~~~~~~~~~~~~~~~~~~~

    def add_assignment(self,
                       name,
                       release,
                       due,
                       template_file,
                       student_submissions = True,
                       late_submissions = False,
                       group_submissions = 0):
        self._check_capabilities({LoadedCapabilities.ASSIGNMENTS})
        
        assignment_resp = self.session.get('https://www.gradescope.com/courses/'+self.cid+'/assignments')
        parsed_assignment_resp = BeautifulSoup(assignment_resp.text, 'html.parser')
        authenticity_token = parsed_assignment_resp.find('meta', attrs = {'name': 'csrf-token'} ).get('content')

        # TODO Make this less brittle and make sure to support all options properly
        assignment_params = {
            "authenticity_token" : authenticity_token,
            "assignment[title]" : name,
            "assignment[student_submission]" : student_submissions,
            "assignment[release_date_string]" : release,
            "assignment[due_date_string]" : due,
            "assignment[allow_late_submissions]" : 1 if late_submissions else 0,
            "assignment[submission_type]" : "image", # TODO What controls this?
            "assignment[group_submission]" : group_submissions
        }
        assignment_files = {
            "template_pdf" : open(template_file, 'rb')
        }
        assignment_resp = self.session.post('https://www.gradescope.com/courses/'+self.cid+'/assignments',
                                            files = assignment_files,
                                            data = assignment_params)

        # TODO this is highly wasteful, need to likely improve this. 
        self.assignments = {}
        self._lazy_load_assignments()
        
    def remove_assignment(self, name):
        self._check_capabilities({LoadedCapabilities.ASSIGNMENTS})
        
        assignment_resp = self.session.get('https://www.gradescope.com/courses/'+self.cid+'/assignments/'
                                           +self.assignments[name].aid+'/edit')
        parsed_assignment_resp = BeautifulSoup(assignment_resp.text, 'html.parser')
        authenticity_token = parsed_assignment_resp.find('meta', attrs = {'name': 'csrf-token'} ).get('content')

        remove_params = {
            "_method" : "delete",
            "authenticity_token" : authenticity_token
        }

        remove_resp = self.session.post('https://www.gradescope.com/courses/'+self.cid+'/assignments/'
                                     +self.assignments[name].aid,
                                     data = remove_params)

        # TODO this is highly wasteful, need to likely improve this. 
        self.assignments = {}
        self._lazy_load_assignments()

    # ~~~~~~~~~~~~~~~~~~~~~~HOUSEKEEPING~~~~~~~~~~~~~~~~~~~~~~~~~

    def _lazy_load_assignments(self):
        '''
        Load the assignment dictionary from assignments. This is done lazily to avoid slowdown caused by getting
        all the assignments for all classes. Also makes us less vulnerable to blocking.
        '''
        assignment_resp = self.session.get('https://www.gradescope.com/courses/'+self.cid+'/assignments')
        parsed_assignment_resp = BeautifulSoup(assignment_resp.text, 'html.parser')
        
        assignment_table = []
        for assignment_row in parsed_assignment_resp.findAll('tr', class_ = 'js-assignmentTableAssignmentRow'):
            row = []
            for td in assignment_row.findAll('td'):
                row.append(td)
            assignment_table.append(row)
        
        for row in assignment_table:
            name = row[0].text
            aid = row[0].find('a').get('href').rsplit('/',1)[1]
            points = row[1].text
            # TODO: (released,due) = parse(row[2])
            submissions = row[3].text
            percent_graded = row[4].text
            complete = True if 'workflowCheck-complete' in row[5].get('class') else False
            regrades_on  = False if row[6].text == 'OFF' else True
            # TODO make these types reasonable
            self.assignments[name] = GSAssignment(name, aid, points, percent_graded, complete, regrades_on, self)
        self.state.add(LoadedCapabilities.ASSIGNMENTS)
        pass

    def _lazy_load_roster(self):
        '''
        Load the roster list. This is done lazily to avoid slowdown caused by getting
        all the rosters for all classes. Also makes us less vulnerable to blocking.
        '''
        membership_resp = self.session.get('https://www.gradescope.com/courses/' + self.cid + '/memberships')
        parsed_membership_resp = BeautifulSoup(membership_resp.text, 'html.parser')

        roster_table = []
        for student_row in parsed_membership_resp.find_all('tr', class_ = 'rosterRow'):
            row = []
            for td in student_row('td'):
                row.append(td)
            roster_table.append(row)
        
        for row in roster_table:
            name = row[0].text.rsplit(' ', 1)[0]
            data_id = row[0].find('button', class_ = 'rosterCell--editIcon').get('data-id')
            if len(row) == 7: # TODO: Adjusted to 7 columns
                email = row[1].text
                role = row[2].find('option', selected="selected").text
                submissions = int(row[3].text)
                linked = True if 'statusIcon-active' in row[4].find('i').get('class') else False
            else:
                email = row[2].text
                role = row[3].find('option', selected="selected").text
                submissions = int(row[4].text)
                linked = True if 'statusIcon-active' in row[5].find('i').get('class') else False
            # TODO Make types reasonable.
            self.roster[data_id] = GSPerson(name, data_id, email, role, submissions, linked)
        self.state.add(LoadedCapabilities.ROSTER)
        
    def _lazy_load_grades(self):
        '''
        Load grades for all students. This is done lazily to avoid slowdown caused by getting
        all the grades for all classes. Also makes us less vulnerable to blocking.
        '''
        print('loading grades')
        self._check_capabilities({LoadedCapabilities.ASSIGNMENTS, LoadedCapabilities.ROSTER}) # we need data to create grades later
        membership_resp = self.session.get('https://www.gradescope.com/courses/' + self.cid + '/memberships')
        parsed_membership_resp = BeautifulSoup(membership_resp.text, 'html.parser')

        roster_table = []
        for student_row in parsed_membership_resp.find_all('tr', class_ = 'rosterRow'):
            row = []
            for td in student_row('td'):
                row.append(td)
            roster_table.append(row)
        
        for row in roster_table:
            name = row[0].text.rsplit(' ', 1)[0]
            data_id = row[0].find('button', class_ = 'rosterCell--editIcon').get('data-id')
            
            # Get url to gradebook data. Only students has a js-rosterName tag, so we skip professors
            try:
                grade_url = row[0].find('button', class_ = 'js-rosterName').get('data-url')
            except:
                continue
            # Request gradebook data. Retry once then skip if continuing to fail
            try:
                gradebook_resp = self.session.get('https://www.gradescope.com' + grade_url)
            except:
                print('@Error - requesting grade data failed. Retrying once')
                try: # TODO: This is a janky retry. If a roster is huge it might become an issue if we're spamming gradescope
                    time.sleep(3)
                    gradebook_resp = self.session.get('https://www.gradescope.com' + grade_url)
                except:
                    continue
            # Parse response and create grade objects
            parsed_gradebook_resp = BeautifulSoup(gradebook_resp.text, 'html.parser')
            print(parsed_gradebook_resp)
            grade_json = json.loads(parsed_gradebook_resp.text)
            self.grades[data_id] = {} # TODO: This indexes students by their data_id. This is probably more consistant and less error prone to duplication. I should probably switch roster to this
            for grade in grade_json:
                assign = grade['assignment']
                self.grades[data_id][assign['title']] = GSGrade(name, assign['title'], assign['id'], assign['total_points'], assign['submission']['score'], assign['submission']['url'])
        self.state.add(LoadedCapabilities.GRADES)

    def _check_capabilities(self, needed):
        '''
        checks if we have the needed data loaded and gets them lazily.
        '''
        missing = needed - self.state
        if LoadedCapabilities.ASSIGNMENTS in missing:
            self._lazy_load_assignments()
        if LoadedCapabilities.ROSTER in missing:
            self._lazy_load_roster()
        if LoadedCapabilities.GRADES in missing:
            self._lazy_load_grades()
    
    def _force_load_data(self):
        '''
        dumps existing data and force loads it
        '''
        self.assignments = {}
        self.roster = {}
        self.grades = {}
        self._lazy_load_assignments()
        self._lazy_load_roster()
        self._lazy_load_grades()
        self.state.add(LoadedCapabilities.ASSIGNMENTS)
        self.state.add(LoadedCapabilities.ROSTER)
        self.state.add(LoadedCapabilities.GRADES)
        

    def delete(self):
        course_edit_resp = self.session.get('https://www.gradescope.com/courses/'+self.cid+'/edit')
        parsed_course_edit_resp = BeautifulSoup(course_edit_resp.text, 'html.parser')

        authenticity_token = parsed_course_edit_resp.find('meta', attrs = {'name': 'csrf-token'} ).get('content')

        print(authenticity_token)

        delete_params = {
            "_method": "delete",
            "authenticity_token": authenticity_token
        }
        print(delete_params)

        delete_resp = self.session.post('https://www.gradescope.com/courses/'+self.cid,
                                        data = delete_params,
                                        headers={
                                            'referer': 'https://www.gradescope.com/courses/'+self.cid+'/edit',
                                            'origin': 'https://www.gradescope.com'
                                        })
        
        # TODO make this less brittle 
