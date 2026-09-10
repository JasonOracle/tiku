import re
t = open(r'D:\project\tiku\tiku\tob\src\views\model-center\ModelCenterView.vue', encoding='utf-8').read()
print(len(t.splitlines()), 'lines')
for i, l in enumerate(t.splitlines()):
    s = l.strip()
    if re.search(r'request\.|/api/v1/', s):
        print('  ', i + 1, s[:140])
