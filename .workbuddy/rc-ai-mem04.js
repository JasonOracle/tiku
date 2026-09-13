async (page) => {
  const PH = '输入问题... (Enter 发送，Shift+Enter 换行)';
  const ta = page.getByPlaceholder(PH);
  const rowsText = () => page.evaluate(() => Array.from(document.querySelectorAll('.assistant-row')).map(e => e.innerText.trim()));
  const waitStable = async (maxWait = 150000) => {
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
  const ask = async (id, q) => {
    await ta.click(); await ta.fill(q); await page.waitForTimeout(400); await ta.press('Enter');
    await waitStable();
    const rows = await rowsText();
    return { id, q, last: rows[rows.length - 1] };
  };
  try { await page.getByRole('button', { name: '新建对话' }).click(); await page.waitForTimeout(1500); } catch (e) {}
  const out = [];
  out.push(await ask('MEM-04', '你记得我平时喜欢出什么难度的题吗？'));
  return JSON.stringify(out, null, 2);
}
