import os, re, sys
results = []
for root, dirs, files in os.walk('core/skills'):
    for f in files:
        if f == 'SKILL.md':
            results.append(os.path.join(root, f))
results.sort()
for fpath in results:
    name = os.path.basename(os.path.dirname(fpath))
    with open(fpath, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    total = len(lines)
    desc = ''
    in_front = False
    front_done = False
    sections = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s == '---':
            if not in_front: in_front = True
            else: in_front = False; front_done = True
            continue
        if in_front:
            m = re.match(r'^description:\s*(.*)', s, re.IGNORECASE)
            if m: desc = m.group(1)
        if front_done and not in_front:
            if s.startswith('## '):
                sections.append(s[3:].strip())
            elif i + 1 < total:
                nxt = lines[i + 1].strip()
                if re.match(r'^=+$', nxt) and s != '':
                    sections.append(s.strip())
    sec = ', '.join(sections)
    sys.stdout.write(f'{name} | description: {desc} | sections: {sec} | lines: {total}\n')
sys.stdout.flush()
