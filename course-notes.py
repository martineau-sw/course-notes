import sys
import os


def parse_line(line):

    content = line.split(":")
    section = (content[0].split()[1].strip()
               if len(content) > 1 and line.find("Section") >= 0
               else "0")
    lesson = (content[0].split()[1].strip()
              if len(content) > 1 and line.find("Lesson") >= 0
              else "0")

    return (section, lesson, line.strip())


def format_path(*nodes):
    strings = []
    for node in nodes:
        if node is not None:
            strings.append(node.lower().replace(" ", "-"))
    return "/".join(strings)


def format_file_name(*names):
    strings = []
    for name in names:
        if name is not None:
            strings.append(name.lower().replace(" ", "-"))
    return "-".join(strings)


class Note:

    def __init__(self, source, course, name, section, lesson):
        self.source = source
        self.course = course
        self.name = name
        self.section = "0" if section is None else section
        self.lesson = "0" if lesson is None else lesson
        self.tags = []
        self.aliases = []
        self.children = []

    @classmethod
    def from_string(cls, source, course, string):
        section, lesson, name = parse_line(string)
        return cls(source, course, name, section, lesson)

    def is_section(self):
        return self.name.find("Section") >= 0

    def is_lesson(self):
        return self.name.find("Lesson") >= 0

    def add_tag(self, string):
        self.tags.append(string)

    def add_alias(self, string):
        self.aliases.append(f'"{string}"')

    def add_child(self, note):
        self.children.append(note)

    def to_path_string(self):
        if self.section != "0":
            return format_path(
                    self.source,
                    self.course,
                    self.section,
                    self.lesson)
        return format_path(
                self.source,
                self.course,
                self.section)

    def to_kebab_string(self):
        return format_file_name(self.section, self.lesson, self.get_title())

    def get_title(self):
        return self.name.split(":")[-1].strip()

    def get_md_tags(self):
        string = "tags:\n"
        for tag in self.tags:
            string += f"  - {tag}\n"
        return string

    def get_md_aliases(self):
        string = "aliases:\n"
        for alias in self.aliases:
            string += f"  - {alias}\n"
        return string

    def get_md_properties(self):
        return (
            "---\n"
            f"{self.get_md_tags()}"
            f"{self.get_md_aliases()}"
            f"{self.get_md_children()}"
            "---\n"
        )

    def get_md_children(self):
        if len(self.children) > 0:
            string = "lessons:\n" if self.is_section() else "sections:\n"
            for child in self.children:
                link = f'"[[{child.to_kebab_string()}|{child.name}]]"'
                string += f"  - {link}\n"
            return string
        return ""

    def to_file(self, folder):
        file_name = f"./{folder}/{self.to_kebab_string()}.md"
        file_props = self.get_md_properties()
        file_content = f"# {self.get_title()}\n"
        file = open(file_name, "x")
        file.write(file_props)
        file.write(file_content)
        file.close()


if len(sys.argv) != 2 or not sys.argv[1].endswith(".crs"):
    print("Specify .crs file")
    sys.exit()

try:
    notes_structure = open(sys.argv[1], "r")
except IOError:
    print(f"Could not open {sys.argv[1]}")
    sys.exit()

notes_lines = notes_structure.readlines()

institution_name = notes_lines[0].rstrip()
course_code = notes_lines[1].split()[0].strip()
course_name = notes_lines[1][len(course_code) + 1:].strip()

notes = []

course_note = Note(institution_name, course_code, course_name, "0", "0")
course_note.add_tag(course_note.to_path_string())
course_note.add_alias(course_note.name)
notes.append(course_note)

current_section = None

for line in notes_lines[2:]:
    note = Note.from_string(institution_name, course_code, line)

    if note.is_section():
        current_section = note
        notes[0].add_child(current_section)
    elif note.is_lesson():
        note.section = current_section.section
        current_section.add_child(note)

    note.add_tag(note.to_path_string())
    note.add_alias(note.name)
    notes.append(note)

os.mkdir(f"./{course_name.lower().replace(" ", "-")}")
print(os.getcwd())
for note in notes:
    note.to_file(course_name.lower().replace(" ", "-"))
