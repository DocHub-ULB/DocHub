import time

from bs4 import BeautifulSoup
import requests
import json

start = time.time()
times = []
limit_to = 350

URL = f"https://www.ulb.be/servlet/search?l=0&beanKey=beanKeyRechercheFormation&&types=formation&natureFormation=ulb&RH=1571625036018525&s=FACULTE_ASC&limit={limit_to}"

print("Getting page")
page = requests.get(URL)
print("done, parsing", round(time.time() - start, 2))

soup = BeautifulSoup(page.content, 'html.parser')
all_courses: list = []

for span in soup.find_all("span", {"class": "search-result__mnemonique"}):
    if span.text not in [course["MNEMO"] for course in all_courses]:
        fac = span.find_previous_siblings("a")
        program_name = span.find_previous("strong", "search-result__structure-intitule").text
        facs: list = []
        for elem in fac:
            children = elem.findChildren()
            facs.append(
                {
                    "color": children[0]["style"][-7:],
                    "name": children[1].text
                }
            )
        all_courses.append(
            {
                "MNEMO": span.text,
                "name": program_name,
                "FAC": facs
            }
        )

print("parsing courses")
for index, course in enumerate(all_courses):
    print(f"({index+1}/{limit_to}) requesting", course['MNEMO'].upper())
    start = time.time()
    programme = None
    while programme is None:
        URL = f"https://www.ulb.be/api/formation?path=%2Fws%2Fksup%2Fprogramme%3Fgen%3Dprod%26anet%3D{course['MNEMO'].upper()}%26lang%3Dfr%26&_=1623514050845"
        try:
            programme = requests.get(URL)
        except Exception:
            print("Error while retreiving", URL)
            programme = None
            time.sleep(5)
    times.append(time.time() - start)
    print("Got, treating", round(time.time() - start, 2))

    try:
        programme_json = json.loads(programme.json()['json'])
        all_courses[index]["courses"] = {}
        for course in programme_json['blocs'][-1]['progCourses']:
            if course['id'] not in ['TEMP-0000', 'HULB-0000']:
                all_courses[index]["courses"][course['id']] = {
                    "id": course['id'],
                    "title": course['title'],
                    "mandatory": course['mandatory'],
                    "bloc": course['bloc'],
                    "lecturers": course['lecturers'],
                    "quadri": course['quadri'],
                }
    except Exception as e:
        print("Error", e)


with open("catalog/management/parser/data/courses.json", "w+") as all_courses_json:
    json.dump(all_courses, all_courses_json, indent=2)

print("Avg. duration:", sum(times) / len(times))
