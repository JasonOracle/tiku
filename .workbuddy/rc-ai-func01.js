async (page) => {
  const PH = '输入问题... (Enter 发送，Shift+Enter 换行)';
  const ta = page.getByPlaceholder(PH);
  const rowsText = () => page.evaluate(() => Array.from(document.querySelectorAll('.assistant-row')).map(e => e.innerText.trim()));
  const lastBtns = () => page.evaluate(() => { const r = document.querySelectorAll('.assistant-row'); const l = r[r.length - 1]; return l ? Array.from(l.querySelectorAll('button')).map(b => (b.innerText || '').trim()).filter(Boolean) : []; });
  const waitStable = async (maxWait = 180000) => {
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
  try { await page.getByRole('button', { name: '新建对话' }).click(); await page.waitForTimeout(1500); } catch (e) {}
  const q = '帮我出1道关于网络安全的单选题，难度中等';
  await ta.click(); await ta.fill(q); await page.waitForTimeout(400); await ta.press('Enter');
  await waitStable();
  let btns = await lastBtns();
  let confirmed = false;
  if (btns.some(b => b.includes('确认生成'))) {
    await page.getByRole('button', { name: /确认生成/ }).click();
    confirmed = true;
    await page.waitForTimeout(2500);
    await waitStable();
  }
  const rows = await rowsText();
  return JSON.stringify({ confirmed, rowCount: rows.length, last: rows[rows.length - 1], btns: await lastBtns() }, null, 2);
}
