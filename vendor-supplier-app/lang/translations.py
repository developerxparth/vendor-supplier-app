import json
def get_translation(lang='en'):
 with open('lang/translations.json', 'r', encoding='utf-8') as f:
  return json.load(f).get(lang)