#@category ReverseEngineering
# Ghidra Jython postScript: statically enumerates function declarations/call sites.
# No target execution and no network access required by this script.
# Invoked only when operator authorizes an already installed Ghidra headless.
import json
import hashlib
args = getScriptArgs()
if len(args) != 1:
    raise ValueError('expected absolute destination JSON path')
manager = currentProgram.getFunctionManager()
functions = []
iterator = manager.getFunctions(True)
for function in iterator:
    if len(functions) >= 25000:
        break
    obj = {'name': function.getName(True), 'address': str(function.getEntryPoint()),
           'evidence_level': 'declared', 'references': []}
    refs = getReferencesTo(function.getEntryPoint())
    for reference in refs[:500] if isinstance(refs, list) else refs:
        if len(obj['references']) >= 500:
            break
        obj['references'].append(str(reference.getFromAddress()))
    functions.append(obj)
with open(args[0], 'w') as output:
    output.write(json.dumps({'format':'ghidra-static', 'source_path':str(currentProgram.getName()),
                             'symbols':functions, 'complete':len(functions)<25000,
                             'evidence':'headless decompiler metadata, call references not dynamic dispatch'},
                            sort_keys=True))
