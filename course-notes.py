notes_structure = open("sample-course", "r")
notes_lines = notes_structure.readlines()

institution_name = notes_lines[0].rstrip()
course_code = notes_lines[1].split()[0].strip()
course_name = notes_lines[1][len(course_code) + 1:].strip()

print(institution_name, course_code, course_name)


"""
for line in notes_lines:
    
"""    

notes_structure.close()
