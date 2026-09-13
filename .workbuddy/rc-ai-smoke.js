async (page) => {
  const ta = page.getByPlaceholder('输入问题... (Enter 发送，Shift+Enter 换行)');
  await ta.click();
  await ta.fill('你好，请用一句话介绍你自己');
  await page.waitForTimeout(400);
  await ta.press('Enter');
  const getText = () => page.evaluate(() => {
    const r = Array.from(document.querySelectorAll('.assistant-row'));
    return r.length ? r[r.length - 1].innerText.trim() : '';
  });
  let last = '', stable = 0, waited = 0;
  for (let i = 0; i < 120; i++) {
    await page.waitForTimeout(1500);
    waited += 1500;
    const t = await getText();
    const thinking = t.includes('思考中') || t.includes('正在思考') || t.includes('生成中');
    if (!thinking && t && t === last) { stable++; if (stable >= 2) break; } else { stable = 0; }
    last = t;
  }
  const dump = await page.evaluate(() => {
    const asst = Array.from(document.querySelectorAll('.assistant-row')).map(e => e.innerText.trim());
    const user = Array.from(document.querySelectorAll('.user-row')).map(e => e.innerText.trim());
    return { userCount: user.length, asstCount: asst.length, user, asst };
  });
  return JSON.stringify({ waitedMs: waited, ...dump }, null, 2);
}
