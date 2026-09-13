async (page) => {
  const info = await page.evaluate(() => {
    const ta = Array.from(document.querySelectorAll('textarea')).map(t => ({ ph: t.placeholder, cls: t.className }));
    const ce = Array.from(document.querySelectorAll('[contenteditable="true"]')).map(t => ({ cls: t.className }));
    const btns = Array.from(document.querySelectorAll('button')).map(b => (b.innerText || '').trim()).filter(Boolean);
    const inputs = Array.from(document.querySelectorAll('input')).map(i => ({ type: i.type, ph: i.placeholder }));
    return { url: location.href, ta, ce, btns, inputs, text: (document.body.innerText || '').slice(0, 1400) };
  });
  return JSON.stringify(info, null, 2);
}
