import re
for p in [r'D:\project\tiku\tiku\tob\src\views\dashboard\DashboardView.vue',
          r'D:\project\tiku\tiku\tob\src\views\banners\BannersView.vue',
          r'D:\project\tiku\tiku\tob\src\views\messages\MessagesView.vue',
          r'D:\project\tiku\tiku\tob\src\views\audit\AuditView.vue']:
    t = open(p, encoding='utf-8').read()
    print('=' * 25, p.split('\\')[-1], len(t.splitlines()))
    for i, l in enumerate(t.splitlines()):
        s = l.strip()
        if re.search(r'request\.(get|post|put|delete)|/api/v1/', s):
            print('  ', i + 1, s[:140])
