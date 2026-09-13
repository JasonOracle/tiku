async (page) => {
  await page.getByRole('button', { name: '录入成员' }).click();
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: '* 手机号' }).fill('13911111109');
  await page.getByRole('textbox', { name: '姓名', exact: true }).fill('RCTEST');
  await page.waitForTimeout(600);
  await page.getByRole('button', { name: '保存' }).click();
  await page.waitForTimeout(2500);
}
