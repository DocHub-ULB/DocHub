from typing import Optional

import os


def get_env(secret_name: str, default: str | None = None, required: bool = False):
    """Gathers secrets and envvars from secret provider and environment"""

    result = os.environ.get(secret_name)
    if result is None:
        if required:
            raise Exception("Configuration error")
        return default
    return result


# TODO: this should go into catalog/
def programTypeAndSlug(program) -> tuple:
    """Returns the type of the program (Bachelier, Master, CAP, ...)"""
    # FIXME : Maybe find a more elegant solution to define a program's type ?
    if "bachelier" in program.name.lower():
        return "Bachelier", "aaaaba"
    if "master de spécialisation" in program.name.lower():
        return "Master de spécialisation", "aamas"
    if "master" in program.name.lower():
        return "Master", "aaama"
    if "certificat" in program.name.lower():
        return "Certificat", "cap"
    if "agrégation" in program.name.lower():
        return "Agrégation", "aess"
    else:
        return "Autre", "zaut"


# TODO: this should go into catalog/
def buildOrderedProgramList(programs) -> list:
    """Builds a list of program types (Bachelier, Master, CAP) with the corresping programs in it"""
    program_dict: dict = {}

    for program in programs:
        program_type, type_slug = programTypeAndSlug(program)
        if type_slug not in program_dict.keys():
            program_dict[type_slug] = {
                "name": program_type,
                "slug": type_slug,
                "programs": [program],
            }
        else:
            program_dict[type_slug]["programs"].append(program)

    return sorted(
        (program for _, program in program_dict.items()), key=lambda x: x["slug"]
    )
