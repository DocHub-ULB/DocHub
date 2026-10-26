"""Check a folder picked for a bulk upload, before any file is sent.

The browser sends only the file paths and sizes. We tell the user which files
will go to which course, and which files we will skip and why. The files
themselves are sent later, one request per file: the server then finds the
files that are already on DocHub.

The folder layout we expect, where "export" is the folder the user picked:

    export/info-f101/TP1.pdf       -> goes to INFO-F101
    export/info-f101/tp/TP2.pdf    -> goes to INFO-F101 (subfolders are fine)
    export/INFO-F101_Algo/TP3.pdf  -> goes to INFO-F101 (text after the code is fine)
    export/notes.pdf               -> not in a course folder, we skip it

If the user picks one course folder directly ("info-f101/tp/TP1.pdf"),
all its files go to that course.
"""

import difflib
import enum
import re
from dataclasses import dataclass, field

from django.conf import settings

from catalog.models import Course
from documents.logic import (
    document_tags,
    document_title,
    split_course_code,
    tag_names_from_name,
)

MAX_FILES = 2000

# Files that the operating system adds by itself. We skip them without a word.
SYSTEM_FILES = {".ds_store", "thumbs.db", "desktop.ini"}


class FileStatus(enum.StrEnum):
    READY = "ready"
    # We skip these, see plan_bulk_upload.
    COMPRESSED = "compressed"
    EMPTY = "empty"


@dataclass
class BulkFile:
    # The path the browser gave us, so that the page can find the file again.
    path: str
    name: str
    size: int
    status: FileStatus = FileStatus.READY
    # The title and the tags that the document will get, see add_file_to_course.
    title: str = ""
    tags: list[str] = field(default_factory=list)

    def describe(self, course: Course) -> None:
        self.title = document_title(self.name, course)
        self.tags = sorted(document_tags(self.name) or tag_names_from_name(self.title))


@dataclass
class BulkFolder:
    name: str
    course: Course | None = None
    suggestion: str = ""
    files: list[BulkFile] = field(default_factory=list)
    # True for the files that lie directly in the folder that the user picked.
    is_picked_folder: bool = False

    @property
    def ready_files(self) -> list[BulkFile]:
        if self.course is None:
            return []
        return [file for file in self.files if file.status == FileStatus.READY]


@dataclass
class BulkPlan:
    folders: list[BulkFolder]

    @property
    def course_folders(self) -> list[BulkFolder]:
        return [folder for folder in self.folders if folder.course is not None]

    @property
    def unknown_folders(self) -> list[BulkFolder]:
        return [
            folder
            for folder in self.folders
            if folder.course is None and not folder.is_picked_folder
        ]

    @property
    def loose_files(self) -> list[BulkFile]:
        """The files that are not in a course folder."""
        return [
            file
            for folder in self.folders
            if folder.course is None and folder.is_picked_folder
            for file in folder.files
        ]

    @property
    def ready_folders(self) -> list[BulkFolder]:
        """The course folders with at least one file to send."""
        return [folder for folder in self.folders if folder.ready_files]

    @property
    def archived_folders(self) -> list[BulkFolder]:
        return [
            folder
            for folder in self.ready_folders
            if folder.course and folder.course.is_archive
        ]

    @property
    def ready_files(self) -> list[BulkFile]:
        return [file for folder in self.folders for file in folder.ready_files]

    @property
    def ready_size(self) -> int:
        return sum(file.size for file in self.ready_files)

    @property
    def ready_course_count(self) -> int:
        return len({folder.course.pk for folder in self.ready_folders if folder.course})

    def files_with_status(self, status: FileStatus) -> list[BulkFile]:
        return [
            file
            for folder in self.course_folders
            for file in folder.files
            if file.status == status
        ]

    @property
    def compressed_files(self) -> list[BulkFile]:
        return self.files_with_status(FileStatus.COMPRESSED)

    @property
    def empty_files(self) -> list[BulkFile]:
        return self.files_with_status(FileStatus.EMPTY)


def is_system_file(parts: list[str]) -> bool:
    return (
        parts[-1].lower() in SYSTEM_FILES
        or parts[-1].startswith("._")
        or "__MACOSX" in parts
    )


def group_by_folder(
    entries: list[tuple[str, int]], picked_is_course: bool
) -> dict[str, list[BulkFile]]:
    """Sort the files by the course folder they are in, see the module docstring."""
    folders: dict[str, list[BulkFile]] = {}
    for path, size in entries:
        parts = [part for part in path.split("/") if part]
        if len(parts) < 2 or is_system_file(parts):
            continue
        folder = parts[0] if picked_is_course or len(parts) == 2 else parts[1]
        folders.setdefault(folder, []).append(BulkFile(path, parts[-1], size))
    for files in folders.values():
        files.sort(key=lambda file: file.path.lower())
    return folders


def find_courses(folder_names: list[str]) -> dict[str, Course]:
    """The course of each folder, from the course code at the start of its name."""
    slugs = {}
    for name in folder_names:
        code, _ = split_course_code(name)
        if code:
            slugs[name] = code
    courses = Course.objects.in_bulk(slugs.values(), field_name="slug")
    return {name: courses[slug] for name, slug in slugs.items() if slug in courses}


def suggest_slug(folder_name: str, all_slugs: list[str]) -> str:
    """A course code close to a folder name that looks like a typo.

    A valid code like "info-f310" is not a typo, even if we do not know
    that course: "info-f530" is another course, not a fix.
    """
    code, _ = split_course_code(folder_name)
    if code:
        return ""
    first_word = re.split(r"[_ ]", folder_name.strip(), maxsplit=1)[0].lower()
    matches = difflib.get_close_matches(first_word, all_slugs, n=1, cutoff=0.85)
    return matches[0] if matches else ""


def plan_bulk_upload(entries: list[tuple[str, int]]) -> BulkPlan:
    picked_folders = {path.split("/")[0] for path, _ in entries}
    picked_is_course = len(picked_folders) == 1 and bool(
        find_courses(list(picked_folders))
    )
    grouped = group_by_folder(entries, picked_is_course)
    courses = find_courses(list(grouped))

    folders = []
    for name, files in sorted(grouped.items(), key=lambda item: item[0].lower()):
        folder = BulkFolder(
            name,
            courses.get(name),
            files=files,
            is_picked_folder=name in picked_folders and not picked_is_course,
        )
        folders.append(folder)
        if folder.course is None:
            continue
        for file in files:
            if file.name.lower().endswith(settings.REJECTED_FILE_FORMATS):
                file.status = FileStatus.COMPRESSED
            elif file.size == 0:
                file.status = FileStatus.EMPTY
            else:
                file.describe(folder.course)

    plan = BulkPlan(folders)
    if plan.unknown_folders:
        all_slugs = list(Course.objects.values_list("slug", flat=True))
        for folder in plan.unknown_folders:
            folder.suggestion = suggest_slug(folder.name, all_slugs)
    return plan
