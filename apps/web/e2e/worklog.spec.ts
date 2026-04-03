import { test, expect, Page } from "@playwright/test";
import { format } from "date-fns";

// 테스트용 로그인 헬퍼
async function loginAs(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.fill('input[id="email"]', email);
  await page.fill('input[id="password"]', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });
}

// E2E 테스트용 계정 (사전에 생성된 테스트 계정 가정)
const E2E_EMAIL = process.env.E2E_EMAIL ?? "e2e@grovarc.dev";
const E2E_PASSWORD = process.env.E2E_PASSWORD ?? "E2eTest1234!";

test.describe("작업 로그", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_EMAIL, E2E_PASSWORD);
  });

  test("로그 작성 → 목록 확인", async ({ page }) => {
    await page.goto("/logs/new");

    const today = format(new Date(), "yyyy-MM-dd");
    const title = `E2E 테스트 로그 ${Date.now()}`;

    await page.fill('input[id="logDate"]', today);
    await page.fill('input[id="title"]', title);
    await page.fill("textarea", "Playwright로 자동 작성된 테스트 로그입니다.");

    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/logs$/, { timeout: 10_000 });
    await expect(page.getByText(title)).toBeVisible();
  });

  test("로그 목록 → 상세 페이지 이동", async ({ page }) => {
    await page.goto("/logs");

    const firstLog = page.locator("ul li a").first();
    await expect(firstLog).toBeVisible();
    await firstLog.click();

    await expect(page).toHaveURL(/\/logs\/[a-z0-9-]+/);
  });

  test("로그 수정", async ({ page }) => {
    await page.goto("/logs");

    await page.locator("ul li a").first().click();
    await expect(page).toHaveURL(/\/logs\/[a-z0-9-]+/);

    await page.getByRole("button", { name: "수정" }).click();

    const updatedTitle = `수정된 제목 ${Date.now()}`;
    await page.fill('input[id="title"]', updatedTitle);
    await page.getByRole("button", { name: "저장" }).click();

    await expect(page.getByText(updatedTitle)).toBeVisible({ timeout: 5_000 });
  });

  test("사이드바 네비게이션 — 로그 → 대시보드 이동", async ({ page }) => {
    await page.goto("/logs");
    await page.getByRole("link", { name: "대시보드" }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
