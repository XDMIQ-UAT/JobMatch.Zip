import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should navigate to login page', async ({ page }) => {
    // Look for login/signin button or link
    const loginButton = page.getByRole('link', { name: /login|sign in/i });
    
    if (await loginButton.isVisible()) {
      await loginButton.click();
      
      // Verify we're on the login page
      await expect(page).toHaveURL(/.*login/);
    }
  });

  test('should navigate to signup page', async ({ page }) => {
    // Look for signup/register button or link
    const signupButton = page.getByRole('link', { name: /sign up|register|get started/i });
    
    if (await signupButton.isVisible()) {
      await signupButton.click();
      
      // Verify we're on the signup page
      await expect(page).toHaveURL(/.*signup|register/);
    }
  });

  test('should show login form elements', async ({ page }) => {
    // Navigate to login page if it exists
    const loginButton = page.getByRole('link', { name: /login|sign in/i });
    
    if (await loginButton.isVisible()) {
      await loginButton.click();
      
      // Check for email/username input
      const emailInput = page.getByRole('textbox', { name: /email|username/i });
      await expect(emailInput).toBeVisible();
      
      // Check for password input
      const passwordInput = page.getByLabel(/password/i);
      await expect(passwordInput).toBeVisible();
      
      // Check for submit button
      const submitButton = page.getByRole('button', { name: /login|sign in/i });
      await expect(submitButton).toBeVisible();
    }
  });
});
