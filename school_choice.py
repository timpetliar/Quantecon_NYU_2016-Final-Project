
# coding: utf-8

# In[4]:

import csv
import numpy as np
from queue import Queue


class School_Choice:
    """
    This class implements the Gale_Shipley Deferred Acceptance Algorithm, with respect to school choice. Although,
    the variable names are thus idiosyncratic, the code is completely general. To implement this code, 
    data should be provided as 1-based index matrices of student preferences and school preferences, as four CSV files
    containing student preferences, school preferences over acceptable applicants, school lists of unacceptable
    applicants, and quotas for each school. Additionally, a test set of data is already written into the class.
    
    ----------------------------------------------------------------------------------------------------
    Necassary parameters are the number of students and the number of schools.
    
   Initialization : Instance = School_Choice(num_students = Interger Value, num_schools = Integer Value)
   
   NOTE: Attribute debug_print = TRUE by DEFAULT. Returns detailed step-by-step results that shows how algorithm works.
   If this is not desired, should be turned of manually, by writing Instace.debug_print = FALSE after instance created.
    
    Methods: 
        
      - Instance.read_data() SEE SEPERATE INFO FOR THIS METHOD
    
      - Instance.execute(), computes the matching
      
      -Instance.print_results_by_schools(), this method prints the match list for each school and the list
      of unmatched students. Results are 0-based (to be consistent with the debug print information)!
   
""" 
    
    #test data. Rows represent students. Columns represent student school preferences.
    _test_student_data_input = np.array(([1, 2, 3],
                                  [1, 3, 2],
                                  [3, 1, 2],
                                  [1, 3, 2],
                                  [2, 3, 1],
                                  [3, 1, 2],
                                  [2, 1, 3],
                                  [2, 0, 0]
                                 ))
    
    # Rows represent schools. Columns represent school's preferences over students.
    _test_school_data_input = np.array(([1, 2, 3 ,4, 5, 6, 7, 0],
                                 [1, 3, 4, 7, 5, 6, 2, 0],
                                 [1, 6, 4, 7, 5, 2, 0, 0],
                                ))
                             
    # Rows represent schools. Columns represent school's unacceptable students.
    _test_school_unacceptable_data_input = np.array(([0, 0, 0 ,0, 0, 0, 0, 0],
                                 [8, 0, 0 ,0, 0, 0, 0, 0],
                                 [3, 0, 0 ,0, 0, 0, 0, 0],
                                ))           
                          
    #Schools' quata     
    #_test_school_quota_input = np.array(([3, 3, 3]))                                                     
    _test_school_quota_input = np.array(([2, 3, 3]))                                                     

    
    
    
    def __init__(self, num_schools, num_students):
            
            #debug print On/Off
            self.debug_print = True
            
            #number of schools participating in match process
            self.num_schools = num_schools
            
            #number of students participating in match process
            self.num_students = num_students
            
            #initialize queue of students
            self._student_queue = Queue(maxsize = num_students)
            
            #create list of student objects and school objects
            self.students = []
            self.schools = []
            self.unmatched_students = [] #indices of students left unmatched at end of algorithm
            
            for i in range(self.num_students):
                self.students.append(Student(i))
            
            for j in range(self.num_schools):
                self.schools.append(School(j))
    
    def read_data(self, data_source, file_names = "", st_data = "", sch_data = "", sch_unacceptable_data = "", sch_quota = ""):
        """
        This method can get data from 3 sources: the internal test data, CSV files, or from matrices passed in
        
        data_source argument :
            'embedded test'  
             'files'
             'input_data' 
         file_names argument:
              empty if data_source argument is embedded test;
              list of csv files (in order of:  
                  student_data, school_data, school_unacceptable_data, school_quota) 
                  if data_source param is file;
         st_data, sch_data, sch_unacceptable_data, sch_quota argumets: input data
        ------------------------------------------------------------------------
Examples:
        
Instance.read_data('files', ["student_data1.csv", "school_data1.csv", "school_unacceptable_data1.csv", "school_quota1.csv"])

Instance.read_data('embedded test')

Passed Matrices: Instace.read_data('input_data', "", student_data, school_data, school_unacceptable_data, school_quota )
        """
        
        if self.debug_print :
            print( "\nread_data(): data_source is ", data_source)

        
        #get input data either from embeded test data or from 'csv' files or as input params
        if data_source == 'embedded test':
            self.student_data_input = self._test_student_data_input
            self.school_data_input = self._test_school_data_input
            self.school_unacceptable_data_input = self._test_school_unacceptable_data_input
            self.school_quota_input = self._test_school_quota_input
        
        elif data_source == 'files':
            #raise ValueError("Error: data source files: not supported yet.")
            
            if (len(file_names)) != 4:
                raise ValueError("read_data(): expect 2nd param as list of 4 file names")
            
            if self.debug_print :
                print( "\nread_data(): list of input files:")
                for i in range(len(file_names)) :
                    print(file_names[i])
            
            
            self.student_data_input = np.empty([self.num_students, self.num_schools], dtype=int)
            self.school_data_input = np.empty([self.num_schools, self.num_students ], dtype=int)
            self.school_unacceptable_data_input = np.empty([self.num_schools, self.num_students ], dtype=int)
            self.school_quota_input = np.empty([self.num_schools], dtype=int)

            
            with open(file_names[0], 'r') as f_st:            
                with open(file_names[1], 'r') as f_sch:        
                    with open(file_names[2], 'r') as f_sch_una:
                        with open(file_names[3], 'r') as f_sch_q:
                            
                            reader_st = csv.reader(f_st)
                            reader_sch = csv.reader(f_sch)
                            reader_sch_una = csv.reader(f_sch_una)
                            reader_sch_q = csv.reader(f_sch_q)
                            
                            if self.debug_print :
                                print( "read_data(): succefully open 4 input files.")
                            
                            #read student data
                            i = -1
                            for row in reader_st :
                                i += 1
                                for j in range(len(row)):
                                    if row[j] == "" :
                                        x = 0
                                    else :   
                                        x = int (row[j]) 
                                    self.student_data_input[i][j] = x
                            
                            #read school data
                            i = -1
                            for row in reader_sch :
                                i += 1
                                for j in range(len(row)):
                                    if row[j] == "" :
                                        x = 0
                                    else :   
                                        x = int (row[j]) 
                                    self.school_data_input[i][j] = x
                                
                            #read school unaccaptable data
                            i = -1
                            for row in reader_sch_una :
                                i += 1
                                for j in range(len(row)):
                                    if row[j] == "" :
                                        x = 0
                                    else :   
                                        x = int (row[j]) 
                                    self.school_unacceptable_data_input[i][j] = x

                            #read school quata
                            for row in reader_sch_q :
                                for j in range(len(row)):
                                    if row[j] == "" :
                                        x = 0
                                    else :   
                                        x = int (row[j]) 
                                    self.school_quota_input[j] = x
                                    
        
        elif data_source == 'input_data':
            #data from numpy matrices passed in
            self.student_data_input = st_data
            self.school_data_input = sch_data
            self.school_unacceptable_data_input = sch_unacceptable_data
            self.school_quota_input = sch_quota
    
        else :
            raise ValueError("Error: illegal data source.")
    
    
        #convert to 0-based indexing
        student_ones = np.ones((self.num_students, self.num_schools), dtype = int) 
        school_ones = np.ones((self.num_schools,self.num_students), dtype = int)
        self.student_data_input = self.student_data_input - student_ones        
        self.school_data_input = self.school_data_input - school_ones
        self.school_unacceptable_data_input = self.school_unacceptable_data_input - school_ones
        
        if self.debug_print :
            print("Input data after converted to 0-based indexing:")
            print("student_data_input:")
            print(self.student_data_input)
            print("school_data_input:")
            print(self.school_data_input)
            print("school_unacceptable_input:")
            print(self.school_unacceptable_data_input)
            print("school_quota_input:")
            print(self.school_quota_input)
        
        
        if self.debug_print :
            print( "\n students data:" )

        for i in range(0, self.num_students):
            
            self.students[i].prefs = list(self.student_data_input[i,:])
            try:
                self.students[i].num_school_choices = self.students[i].prefs.index(-1)           
            except:    
                self.students[i].num_school_choices = len(self.students[i].prefs)   
            
            if self.debug_print :
                print( "self.students[{}].prefs {}".format(i, self.students[i].prefs) )
                print( "self.students[{}].num_school_choices {}".format(i, self.students[i].num_school_choices) ) 
            
            
        if self.debug_print :
            print( "\n schools data:" )
            
        for i in range(0, self.num_schools):
            
            self.schools[i].set_quota( self.school_quota_input[i] )
            self.schools[i].prefs_input = list(self.school_data_input[i,:])
            self.schools[i].unacceptable_input = list(self.school_unacceptable_data_input[i,:])
            self.schools[i].build_prefs_dict()
            
            if self.debug_print :
                print( "self.schools[{}].quota {}".format(i, self.schools[i].quota) )
                print( "self.schools[{}].prefs_input {}".format(i, self.schools[i].prefs_input) )
                print( "self.schools[{}].unacceptable_input {}".format(i, self.schools[i].unacceptable_input) )
                print( "self.schools[{}].prefs_dict {}".format(i, self.schools[i].prefs_dict) )
                print( "")
            
            
    def _init_queue(self):
        
        for i in range(self.num_students):
            self._student_queue.put(i)
        return None
    
    def _IsDone(self):
        
        return self._student_queue.empty()
    
    
    def _step(self):
         
        #Run matching step with one student taken from the queue   
            
        applicant_index = self._student_queue.get()
        applicant = self.students[applicant_index]      
        choice_number = applicant.choice
     
        if self.debug_print :
            print( "step(): applicant={}, choice_number={}".format(applicant_index, choice_number) )
        
        if choice_number >= applicant.num_school_choices: ##### Check >=. school choices start at 0 or 1???
            #student is unmatched once rejected by all choices
            self.unmatched_students.append(applicant_index)
            return None
        
        proposed_school_index = applicant.prefs[choice_number]
        proposed_school = self.schools[proposed_school_index]
        
        #try to add applicant to the school
        ret = proposed_school.add_student(applicant_index)

        if self.debug_print :
            print( "step(): add_student() ret =", ret )

        
        if ret >= 0:
            
            #student with index ret was kicked off from school's match list and should be returned to queue.
            self.students[ret].next_choice()
            self._student_queue.put(ret)
                
        if self.debug_print :
            print( "school =", proposed_school_index, "matches =", proposed_school.matches, "\n" )
            
        return None                        
                
                
                
    def execute(self):
        self._init_queue()
        max_iter = 12 * self.num_students #12 is maximum number of school choices
        counter = 0
        
        if self.debug_print :
            print( "\n execute():")

        while self._IsDone() == False :
            
            self._step()
            
            counter += 1
            
            if counter > max_iter:
                
                raise ValueError("Error: Infinite Loop.")
           
        return None
        

 
    def print_result_by_schools(self):

        print("\nPrint_result_by_schools (note: all indices are 0-based):")
    
        for i in range(0, self.num_schools) :
            print("school =", i, "quota =", self.schools[i].quota, "matches =", self.schools[i].matches)
            
        print ("\n unmatched_students:", self.unmatched_students)
            
        return None
                
                
                    
                
                
                
                
                
                
                
                
                
class Student:
       
        def __init__(self, my_index):
            
            #global student index            
            self.my_index = my_index
        
            #vector of preferences
            self.prefs=[]
            
            #number of schools student has on list
            self.num_school_choices = 0 #will be filled when data read in
             
            #which choice school student will propose    
            self.choice = 0                       
        
        def next_choice(self):
            self.choice +=1
        
            return None
    
class School:
    
    def __init__(self, my_index):

        #debug print On/Off
        self.debug_print = True
        
        #global school index            
        self.my_index = my_index
        
        # number of places available
        self.quota = 0
            
        #preferences over acceptable applicants, sorted by preference. Submitted by school.
        self.prefs_input = []
            
        #Indices of unacceptable students submitted by school. Not necessarily in any particualr order.
        self.unacceptable_input = []
        
        #Dictionary of school preferences over applicants. {Key = student number, Value = school's preference}. 
        # Val = -1 means student is unacceptable.
        self.prefs_dict = {}
            
        # list of students tentativley matched, sorted by school's preference.
        self.matches = []
        
        # number of students currently matched
        self.num_matches = 0
    
    
    def set_quota(self, quota):
        self.quota = quota
        return None
    
    
    def build_prefs_dict(self):
    
        for i in range(len(self.prefs_input)):
            
            if self.prefs_input[i] >= 0:
            
                #add pair {Key = student number, Value = school's preference}
                self.prefs_dict.update( {self.prefs_input[i] : i} )    

        for i in range(len(self.unacceptable_input)):
            
            if self.unacceptable_input[i] >= 0:
                
                #for unacceptable students preference is -1
                #add pair {Key = student number, Value = -1}
                self.prefs_dict.update( {self.unacceptable_input[i] : -1} )    

                
                
        return None    
    
    
    def _get_pref_by_student(self, student_index):
        
        #Takes index of student and returns school's preference for this student
         
        return self.prefs_dict[student_index]

    
    def add_student(self, student_index):
        
        #Function returns: 
        # -1 -student accepted. No one returned to queue.
        # >= 0 -index of student to be returned to queue
        # First, check if student is unacceptable to school. If acceptable, try to add to match list, and eliminate  
        # least preferred student. This will be either the proposing student, or someone from the list.
        
        
        if self.debug_print :
            print( "add_student(): school={}, student={}".format(self.my_index, student_index) )

        
        pref = self._get_pref_by_student(student_index)
        
        if pref == -1:
            
            #student is unacceptable
            return student_index
        
    
        if len(self.matches) == 0:
            
            #list empty. Just add first student
            self.matches.append(student_index)
            return -1
        
        for i in range(len(self.matches)):
            
            #try to find less preferred
            
            student_num = self.matches[i]
            
            if self._get_pref_by_student(student_num) > pref:
                
                #found student less preferred. Add new student before this student.
                self.matches.insert(i, student_index)

              
                if len(self.matches) <= self.quota:
                    
                    #Space still available so no one kicked off the match list
                    
                    return -1
                
                else: 
                    
                    #Number if places exceeded. Eliminate last student from the match list
                    return self.matches.pop()
                    
        #if we are here, there are no less prefferable students in the match list
        if len(self.matches) < self.quota:
            
            #space available, so add new student to end of match list.
            self.matches.append(student_index)
            return -1
        
        else:
            
            #No space available. New student must be returned to queue
            return student_index
            
       
    

    
       


# In[ ]:




# In[ ]:



