from typing import Optional

import os


def get_env(secret_name: str, default: Optional[str] = None):
    """Gathers secrets and envvars from secret provider and environment"""
    if secret_name.startswith("SDC_"):
        # Get secret from a secret provider (portainer ?)
        return ""

    result = os.environ.get(secret_name)
    if result is None:
        return default
    return result


def programTypeAndSlug(program) -> tuple:
    """Returns the type of the program (Bachelier, Master, CAP, ...)"""
    # FIXME : Maybe find a more elegant solution to define a program's type ?
    if "bachelier" in program.name.lower():
        return "Bachelier", "ba"
    if "master de spécialisation" in program.name.lower():
        return "Master de spécialisation", "mas"
    if "master" in program.name.lower():
        return "Master", "ma"
    if "certificat" in program.name.lower():
        return "Certificat", "cap"
    if "agrégation" in program.name.lower():
        return "Agrégation", "aess"
    else:
        return "Autre", "aut"


def buildOrderedProgramList(programs) -> list:
    """Builds a list of program types (Bachelier, Master, CAP) with the corresping programs in it"""
    program_dict: dict = {}

    for program in programs:
        program_type, type_slug = programTypeAndSlug(program)
        if program_type not in program_dict.keys():
            program_dict[program_type] = {
                "name": program_type,
                "slug": type_slug,
                "programs": [program]
            }
        else:
            program_dict[program_type]['programs'].append(program)

    return [program for _, program in program_dict.items()]
