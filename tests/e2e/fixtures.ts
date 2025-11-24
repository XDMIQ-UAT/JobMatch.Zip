import { test as base } from '@playwright/test';

/**
 * Custom fixtures for JobFinder E2E tests
 * Extend these fixtures to add common test setup and utilities
 */

type TestFixtures = {
  authenticatedPage: any;
};

export const test = base.extend<TestFixtures>({
  /**
   * Fixture for authenticated user session
   * Use this when you need to test features that require authentication
   */
  authenticatedPage: async ({ page }, use) => {
    // TODO: Implement authentication logic
    // Example: Login with test credentials
    // await page.goto('/login');
    // await page.fill('[name="email"]', process.env.TEST_USER_EMAIL);
    // await page.fill('[name="password"]', process.env.TEST_USER_PASSWORD);
    // await page.click('button[type="submit"]');
    // await page.waitForURL('/dashboard');
    
    await use(page);
    
    // Cleanup: Logout after test
    // await page.goto('/logout');
  },
});

export { expect } from '@playwright/test';

/**
 * Helper function to wait for API response
 */
export async function waitForApiResponse(page: any, urlPattern: string | RegExp) {
  return page.waitForResponse((response: any) => {
    return response.url().match(urlPattern) && response.status() === 200;
  });
}

/**
 * Helper function to take a screenshot with custom name
 */
export async function takeScreenshot(page: any, name: string) {
  await page.screenshot({ 
    path: `test-results/screenshots/${name}-${Date.now()}.png`,
    fullPage: true 
  });
}
