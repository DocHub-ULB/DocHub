import json

tree: dict = {}
tree["ULB"] = {}
ULB = tree["ULB"]


def get_or_create_fac(fac: dict) -> dict:
    fac_name = fac["name"]
    if fac_name not in ULB:
        ULB[fac_name] = {"name": fac["name"], "color": fac["color"], "programs": {}}
    return ULB[fac_name]


def get_or_create_program(fac: dict, program: dict) -> dict:
    fac = get_or_create_fac(fac)
    program_mnemo = program["mnemo"]
    if program_mnemo not in fac["programs"]:
        fac["programs"][program_mnemo] = {
            "name": program["name"],
            "mnemo": program["mnemo"],
            "blocs": {},
        }
    return fac["programs"][program_mnemo]


def get_or_create_bloc(fac: dict, program: dict, bloc: dict) -> dict:
    fac = get_or_create_fac(fac)
    program = get_or_create_program(fac, program)

    bloc = bloc["val"] if bloc["val"] != "U" else "1"  # type: ignore
    if bloc not in program["blocs"]:
        program["blocs"][bloc] = {"val": bloc, "courses": {}}
    return program["blocs"][bloc]


def get_or_create_course(fac: dict, program: dict, bloc: dict, course: dict) -> dict:
    fac = get_or_create_fac(fac)
    program = get_or_create_program(fac, program)
    bloc = get_or_create_bloc(fac, program, bloc)

    if course["mnemo"] not in bloc["courses"]:
        bloc["courses"][course["mnemo"]] = course
    return bloc["courses"][course["mnemo"]]


def build_tree(all_courses):
    for raw_program in all_courses:
        for f in raw_program["FAC"]:
            fac = get_or_create_fac(f)
            program = {"mnemo": raw_program["MNEMO"], "name": raw_program["name"]}
            program = get_or_create_program(fac, program)
            if "courses" not in raw_program:
                continue
            for course_mnemo, course_info in raw_program["courses"].items():
                bloc = {"val": course_info["bloc"]}
                bloc = get_or_create_bloc(fac, program, bloc)

                course = {
                    "mnemo": course_mnemo,
                    "title": course_info["title"],
                    "mandatory": course_info["mandatory"],
                    "lecturers": course_info["lecturers"],
                    "quadri": course_info["quadri"],
                }
                course = get_or_create_course(fac, program, bloc, course)


with open("catalog/management/parser/data/courses.json") as all_courses_json:
    all_courses = json.load(all_courses_json)
    build_tree(all_courses)

with open("catalog/management/parser/data/tree.json", "w+") as treeson:
    json.dump(tree, treeson, indent=2)
