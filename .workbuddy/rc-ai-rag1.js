async (page) => {
  const PH = '输入问题... (Enter 发送，Shift+Enter 换行)';
  const ta = page.getByPlaceholder(PH);
  const rowsText = () => page.evaluate(() => Array.from(document.querySelectorAll('.assistant-row')).map(e => e.innerText.trim()));
  const lastBtns = () => page.evaluate(() => { const r = document.querySelectorAll('.assistant-row'); const l = r[r.length - 1]; return l ? Array.from(l.querySelectorAll('button')).map(b => (b.innerText || '').trim()).filter(Boolean) : []; });
  const waitStable = async (maxWait = 210000) => {
    let last = '', stable = 0;
    const loops = Math.ceil(maxWait / 1500);
    for (let i = 0; i < loops; i++) {
      await page.waitForTimeout(1500);
      const arr = await rowsText();
      const t = arr.length ? arr[arr.length - 1] : '';
      const thinking = /思考中|正在思考|生成中|处理中|请稍候/.test(t);
      if (t && !thinking && t === last) { stable++; if (stable >= 2) break; } else stable = 0;
      last = t;
    }
    return last;
  };
  const CONFIRM_RE = /确认生成|确认.*入库|确认创建|确认执行/;
  try { await page.getByRole('button', { name: '新建对话' }).click(); await page.waitForTimeout(1500); } catch (e) {}
  const out = [];
  await ta.click(); await ta.fill('出3道火星守则判断题。'); await page.waitForTimeout(400); await ta.press('Enter');
  await waitStable();
  let btns = await lastBtns();
  let confirmed = false;
  for (let k = 0; k < 3; k++) {
    const b = btns.find(x => CONFIRM_RE.test(x));
    if (!b) break;
    await page.getByRole('button', { name: b }).click();
    confirmed = true;
    await page.waitForTimeout(3000);
    await waitStable();
    btns = await lastBtns();
    if (!btns.some(x => CONFIRM_RE.test(x))) break;
  }
  const rows = await rowsText();
  out.push({ id: 'AI-RAG-01', confirmed, btns, last: rows[rows.length - 1] });
  return JSON.stringify(out, null, 2);
}
