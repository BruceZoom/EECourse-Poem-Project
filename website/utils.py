import codecs

DISPLAY_UTILS = {

}

FORM_INIT = {
    'searchType': 'all',
    'query': '',
}

with codecs.open('templates/header.html', 'r', encoding='utf-8') as f:
    HEADER = ''.join(f.readlines())
