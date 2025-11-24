# JobFinder E2E Tests

This directory contains end-to-end (E2E) tests for the JobFinder application using Playwright.

## Directory Structure

```
tests/
├── e2e/                    # E2E test files
│   ├── homepage.spec.ts    # Homepage tests
│   ├── auth.spec.ts        # Authentication flow tests
│   └── fixtures.ts         # Custom test fixtures and utilities
└── README.md              # This file
```

## Quick Start

### 1. Setup Playwright (First Time Only)

```powershell
# Run the setup script
.\scripts\setup-playwright.ps1

# Or manually:
npm install -D @playwright/test
npx playwright install
```

### 2. Configure Environment

Copy `.env.test.example` to `.env.test` and update with your test credentials:

```bash
BASE_URL=http://localhost:3000
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123
```

### 3. Run Tests

```powershell
# Run all tests
npm run test:e2e

# Run tests in UI mode (recommended for development)
npm run test:e2e:ui

# Run tests with visible browser
npm run test:e2e:headed

# Debug tests
npm run test:e2e:debug

# View test report
npm run test:e2e:report
```

## Writing Tests

### Basic Test Example

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/JobFinder/);
  });
});
```

### Using Custom Fixtures

```typescript
import { test, expect } from './fixtures';

test('should access protected route', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/dashboard');
  await expect(authenticatedPage).toHaveURL(/dashboard/);
});
```

## Test Organization

- **homepage.spec.ts** - Tests for the main landing page
- **auth.spec.ts** - Tests for authentication flows (login, signup, logout)
- **fixtures.ts** - Shared test utilities and custom fixtures

Add new test files following the pattern: `[feature].spec.ts`

## Best Practices

1. **Use descriptive test names** - Make it clear what's being tested
2. **Use Page Object Model** - Create page classes for complex interactions
3. **Wait for network requests** - Ensure data is loaded before assertions
4. **Use accessibility selectors** - Prefer `getByRole`, `getByLabel` over CSS selectors
5. **Keep tests independent** - Each test should be able to run in isolation
6. **Use fixtures for setup** - Share common setup logic across tests

## MCP Integration

With Warp's MCP support, you can interact with Playwright directly through AI:

```
You: "Navigate to localhost:3000 and test the login form"
AI: [Uses browser_navigate, browser_type, browser_click MCP tools]
```

Available browser tools:
- Navigation: `browser_navigate`, `browser_navigate_back`
- Interaction: `browser_click`, `browser_type`, `browser_hover`
- Information: `browser_snapshot`, `browser_take_screenshot`
- Advanced: `browser_evaluate`, `browser_run_code`

See [PLAYWRIGHT_MCP_SETUP.md](../docs/PLAYWRIGHT_MCP_SETUP.md) for complete documentation.

## Troubleshooting

### Tests are timing out
- Increase timeout in `playwright.config.ts`
- Ensure frontend is running on port 3000
- Use `await page.waitForLoadState('networkidle')`

### Browser not launching
```powershell
# Reinstall browsers
npx playwright install chromium
```

### Can't find elements
- Use Playwright Inspector: `npx playwright test --debug`
- Use codegen to generate selectors: `npx playwright codegen localhost:3000`

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Full Setup Guide](../docs/PLAYWRIGHT_MCP_SETUP.md)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
