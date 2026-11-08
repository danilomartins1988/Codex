import json,pathlib,sys
p=pathlib.Path(__file__).resolve().parents[1]
d=json.loads((p/'research/claims.json').read_text())
missing=[x['id'] for x in d['claims'] if not x.get('verifiedAgainstRetrievedDocument') or not x.get('evidence')]
if d['status']!='verified' or missing:
 print('BLOCKED: primary-source verification incomplete:',', '.join(missing));sys.exit(1)
print('Editorial claim gate passed.')
