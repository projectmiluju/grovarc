import { test, expect, Page } from "@playwright/test";

async function loginAs(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.fill('input[id="email"]', email);
  await page.fill('input[id="password"]', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });
}

const E2E_EMAIL = process.env.E2E_EMAIL ?? "e2e@grovarc.dev";
const E2E_PASSWORD = process.env.E2E_PASSWORD ?? "E2eTest1234!";

test.describe("회고", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_EMAIL, E2E_PASSWORD);
  });

  test("회고 목록 페이지 진입", async ({ page }) => {
    await page.goto("/retrospectives");
    await expect(page).toHaveURL(/\/retrospectives/);
    await expect(page.getByRole("heading", { name: "회고" })).toBeVisible();
  });

  test("탭 전환 — ALL / PUBLISHED / DRAFT", async ({ page }) => {
    await page.goto("/retrospectives");

    await page.getByRole("tab", { name: "PUBLISHED" }).click();
    await expect(page.getByRole("tab", { name: "PUBLISHED" })).toHaveAttribute(
      "data-state",
      "active",
    );

    await page.getByRole("tab", { name: "DRAFT" }).click();
    await expect(page.getByRole("tab", { name: "DRAFT" })).toHaveAttribute(
      "data-state",
      "active",
    );
  });

  test("회고 상세 페이지 이동", async ({ page }) => {
    await page.goto("/retrospectives");

    const firstItem = page.locator("ul li a").first();
    const hasItem = await firstItem.isVisible();
    if (!hasItem) {
      // 회고가 없으면 테스트 스킵
      return;
    }

    await firstItem.click();
    await expect(page).toHaveURL(/\/retrospectives\/[a-z0-9-]+/);
  });

  test("사이드바 네비게이션 — 회고 → 대시보드", async ({ page }) => {
    await page.goto("/retrospectives");
    await page.getByRole("link", { name: "대시보드" }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
