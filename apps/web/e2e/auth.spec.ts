import { test, expect } from "@playwright/test";

const TEST_EMAIL = `test_${Date.now()}@grovarc.dev`;
const TEST_PASSWORD = "Test1234!";
const TEST_NICKNAME = "테스트유저";

test.describe("인증 플로우", () => {
  test("회원가입 → 자동 로그인 → 대시보드 이동", async ({ page }) => {
    await page.goto("/signup");
    await expect(page).toHaveTitle(/Grovarc/);

    await page.fill('input[id="email"]', TEST_EMAIL);
    await page.fill('input[id="nickname"]', TEST_NICKNAME);
    await page.fill('input[id="password"]', TEST_PASSWORD);
    await page.fill('input[id="passwordConfirm"]', TEST_PASSWORD);

    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });
  });

  test("로그인 성공 → 대시보드 이동", async ({ page }) => {
    await page.goto("/login");

    await page.fill('input[id="email"]', TEST_EMAIL);
    await page.fill('input[id="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });
  });

  test("로그인 실패 → 에러 메시지 표시", async ({ page }) => {
    await page.goto("/login");

    await page.fill('input[id="email"]', "wrong@grovarc.dev");
    await page.fill('input[id="password"]', "wrongpassword");
    await page.click('button[type="submit"]');

    await expect(
      page.getByText("이메일 또는 비밀번호가 올바르지 않습니다"),
    ).toBeVisible({ timeout: 5_000 });
  });

  test("미인증 상태로 대시보드 접근 → 로그인 페이지 리다이렉트", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("로그아웃 → 로그인 페이지 이동", async ({ page }) => {
    // 로그인 먼저
    await page.goto("/login");
    await page.fill('input[id="email"]', TEST_EMAIL);
    await page.fill('input[id="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 });

    // 로그아웃
    await page.getByRole("button", { name: "로그아웃" }).click();
    await expect(page).toHaveURL(/\/login/);
  });
});
