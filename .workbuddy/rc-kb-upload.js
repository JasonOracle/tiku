async (page) => {
  const base = 'D:/project/tiku/tiku/.workbuddy/test-assets/';
  const input = page.locator('input[type=file]');
  await input.setInputFiles(base + '火星员工守则.pdf');
  await page.waitForTimeout(6000);
  await input.setInputFiles(base + '恶意投毒样本.pdf');
  await page.waitForTimeout(6000);
  return 'uploaded';
}
