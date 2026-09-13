async (page) => {
  const info = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button')).map(b => (b.innerText || '').trim()).filter(Boolean);
    const inputs = Array.from(document.querySelectorAll('input')).map(i => ({ type: i.type, accept: i.accept, placeholder: i.placeholder }));
    const hs = Array.from(document.querySelectorAll('h1,h2,h3')).map(e => (e.innerText || '').trim()).filter(Boolean);
    return { url: location.href, btns, inputs, hs, text: (document.body.innerText || '').slice(0, 900) };
  });
  return JSON.stringify(info, null, 2);
}
