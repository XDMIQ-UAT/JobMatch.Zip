import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test('should load the homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/JobMatch/i);
  });

  test('should show Get Started button', async ({ page }) => {
    await page.goto('/');
    const getStartedButton = page.getByRole('button', { name: /get started/i });
    await expect(getStartedButton).toBeVisible();
  });

  test('should open QuickAuth when Get Started is clicked', async ({ page }) => {
    await page.goto('/');
    const getStartedButton = page.getByRole('button', { name: /get started/i });
    await getStartedButton.click();
    
    // Should show QuickAuth component
    await expect(page.getByText(/Quick Authentication/i)).toBeVisible();
    await expect(page.getByText(/Email/i)).toBeVisible();
    await expect(page.getByText(/SMS/i)).toBeVisible();
  });

  test('should allow selecting email authentication', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /get started/i }).click();
    
    // Click email option
    await page.getByText(/Email/i).click();
    
    // Should show email input
    await expect(page.getByPlaceholder(/your@email.com/i)).toBeVisible();
  });

  test('should allow selecting SMS authentication', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /get started/i }).click();
    
    // Click SMS option
    await page.getByText(/SMS/i).click();
    
    // Should show phone input
    await expect(page.getByPlaceholder(/\+1/i)).toBeVisible();
  });
});

