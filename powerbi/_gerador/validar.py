import json, glob, os, sys
from jsonschema import Draft7Validator
from referencing import Registry, Resource
ROOT='/home/claude/ms-schemas/fabric/item/report/definition'
PFX='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'
def retrieve(uri):
    path=os.path.join(ROOT, uri.replace(PFX,''))
    return Resource.from_contents(json.load(open(path)))
reg=Registry(retrieve=retrieve)
bad=0; n=0
for f in glob.glob(sys.argv[1]+'/**/*.json', recursive=True):
    d=json.load(open(f)); s=d.get('$schema')
    if not s or not s.startswith(PFX): continue
    sch=json.load(open(os.path.join(ROOT,s.replace(PFX,''))))
    v=Draft7Validator(sch, registry=reg)
    errs=list(v.iter_errors(d)); n+=1
    for e in errs[:3]:
        bad+=1; print(f, list(e.absolute_path), e.message[:200])
print('arquivos validados:', n, 'erros:', bad)
