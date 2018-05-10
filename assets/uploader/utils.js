const tag_translate = {
    'é': 'e',
    'è': 'e',
    'ê': 'e',
    '-': ' ',
    '_': ' ',
    'û': 'u',
    'ô': 'o',
    'Ã©': 'e',
    'Ã¨': 'e',
    'Ã': 'a',
}

const name_translate = {
    '_': ' ',
    '.': ' ',
    'Ã©': 'é',
    'Ã¨': 'è',
    'Ã': 'à',
}

const tag_mapping = {
    "aout": "examen",
    "sept": "examen",
    "juin": "examen",
    "mai": "examen",
    "exam": "examen",
    "questions": "examen",
    "oral": "examen",
    "corr": "corrigé",
    "reponse": "corrigé",
    "rponse": "corrigé",
    "tp": "tp",
    "pratique": "tp",
    "exo": "tp",
    "exercice": "tp",
    "seance": "tp",
    "enonce": "tp",
    "resum": "résumé",
    "r?sum": "résumé",
    "rsum": "résumé",
    "synthese": "résumé",
    "synthse": "résumé",
    "slide": "slides",
    "transparent": "slides",
    "formule": "formulaire",
    "rapport": "laboratoire",
    "labo": "laboratoire",
    "cahier": "laboratoire",
    "note": "notes",
    "sylabus": "syllabus",
    "syllabus": "syllabus",
    "officiel": "officiel",
    "oficiel": "officiel",
}


export function detect_tags(filename) {
    let name = filename.toLowerCase()

    for (const [search, replacement] of Object.entries(tag_translate)) {
        name = name.split(search).join(replacement)
    }

    let tokens = name.split(' ')
    let tags = new Set()

    for (const token of tokens) {
        for (const [key, value] of Object.entries(tag_mapping)) {
            if(token.includes(key)) {
                tags.add(value)
            }
        }
    }
    console.log(tags)
    return Array.from(tags)
}

export function clean_filename(filename) {
    let extension = filename.substring(filename.lastIndexOf(".") + 1)
    let name = filename.substring(0, filename.lastIndexOf("."))

    if (name.toUpperCase() == name) {
        // if we are in full uppercase
        // .capitalize()
        name = name.charAt(0).toUpperCase() + name.slice(1).toLowerCase()
    }

    for (const [search, replacement] of Object.entries(name_translate)) {
        name = name.split(search).join(replacement)
    }

    return name
}


export function upload_form_data(formData, url){
    fetch(url, {
        method: 'POST',
        body: formData,
      }).then(
        success => console.log(success) // Handle the success response object
      ).catch(
        error => console.log(error) // Handle the error response object
      );
}
