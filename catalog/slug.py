from typing import Callable, List

import re


class Slug:
    def __init__(self, domain: str, faculty: str, number: str):
        self.domain = domain.strip().lower()
        if len(self.domain) > 4:
            raise ValueError("domain may not be longer than 4 chars")
        if not self.domain.isalpha():
            raise ValueError("domain may contain only alphabetic chars")

        self.faculty = faculty.strip().lower()
        if len(self.faculty) != 1:
            raise ValueError("faculty must be only one char long")
        if not self.faculty.isalpha():
            raise ValueError("faculty may contain only alphabetic chars")

        self.number = number.strip().lower()
        if len(self.number) > 4 or len(self.number) < 2:
            raise ValueError("number lenght must be 2, 3 or 4 chars only")
        if not self.number.isdigit():
            raise ValueError("number may contain only digits")

    @property
    def attached(self):
        return f"{self.domain}{self.faculty}{self.number}".upper()

    @property
    def catalog(self):
        return f"{self.domain}-{self.faculty}{self.number}".upper()

    @property
    def dochub(self):
        return f"{self.domain}-{self.faculty}{self.number}".lower()

    @classmethod
    def from_attached(cls, string: str) -> "Slug":
        match = re.match(r"([A-Za-z]+)([A-Za-z])(\d+)", string)
        if match is None:
            raise ValueError("Invalid slug format. Must be like 'INFOF103'")
        domain, faculty, number = match.groups()
        return cls(domain, faculty, number)

    @classmethod
    def from_catalog(cls, string: str) -> "Slug":
        match = re.match(r"([A-Za-z]+)-([A-Za-z])(\d+)", string)
        if match is None:
            raise ValueError("Invalid slug format. Must be like 'INFO-F103'")
        domain, faculty, number = match.groups()
        return cls(domain, faculty, number)

    @classmethod
    def from_dochub(cls, string: str) -> "Slug":
        match = re.match(r"([A-Za-z]+)-([A-Za-z])-(\d+)", string.upper())
        if match is None:
            raise ValueError("Invalid slug format. Must be like 'info-f-103'")
        domain, faculty, number = match.groups()
        return cls(domain, faculty, number)

    @classmethod
    def match_all(cls, string: str):
        for method in [cls.from_catalog, cls.from_dochub, cls.from_attached]:
            try:
                return method(string)
            except ValueError:
                pass

        raise ValueError("Not valid slug found")

    def __repr__(self):
        return f"<Slug: {self}>"

    def __str__(self):
        return self.dochub

    def __eq__(self, other):
        if not isinstance(other, Slug):
            return NotImplemented
        return (self.domain, self.faculty, self.number) == (
            other.domain,
            other.faculty,
            other.number,
        )

    def __hash__(self):
        return hash((self.domain, self.faculty, self.number))


def normalize_slug(slug: str) -> str:
    return Slug.match_all(slug).dochub
