# Playwright Quick Reference

Quick reference for Playwright testing and MCP integration in JobFinder.

## Installation

```powershell
# Automated setup (recommended)
.\scripts\setup-playwright.ps1

# Manual setup
npm install -D @playwright/test
npx playwright install
```

## Common Commands

```powershell
# Run all tests
npm run test:e2e

# Interactive UI mode (best for development)
npm run test:e2e:ui

# Watch browser while testing
npm run test:e2e:headed

# Debug mode (step through tests)
npm run test:e2e:debug

# View HTML report
npm run test:e2e:report

# Run specific test file
npx playwright test tests/e2e/homepage.spec.ts

# Run tests on specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
  });

  test('should do something', async ({ page }) => {
    // Test code here
  });
});
```

## Common Patterns

### Navigation
```typescript
await page.goto('/');
await page.goto('/dashboard');
await page.goBack();
await page.reload();
```

### Selectors (Prefer accessibility-based)
```typescript
// By role (BEST)
await page.getByRole('button', { name: 'Submit' });
await page.getByRole('textbox', { name: 'Email' });

// By label
await page.getByLabel('Email');
await page.getByLabel('Password');

// By placeholder
await page.getByPlaceholder('Enter your email');

// By text
await page.getByText('Welcome');

// CSS selector (use as last resort)
await page.locator('button.submit');
```

### Form Interactions
```typescript
// Fill inputs
await page.fill('input[name="email"]', 'test@example.com');
await page.getByLabel('Email').fill('test@example.com');

// Click buttons
await page.click('button[type="submit"]');
await page.getByRole('button', { name: 'Submit' }).click();

// Select dropdown
await page.selectOption('select', 'value');

// Check checkbox
await page.check('input[type="checkbox"]');

// Upload file
await page.setInputFiles('input[type="file"]', 'path/to/file.pdf');
```

### Waiting
```typescript
// Wait for navigation
await page.waitForURL(/.*dashboard/);

// Wait for network idle
await page.waitForLoadState('networkidle');

// Wait for selector
await page.waitForSelector('.content');

// Wait for API response
await page.waitForResponse(response => 
  response.url().includes('/api/user') && response.status() === 200
);

// Custom wait
await page.waitForTimeout(1000); // Not recommended
```

### Assertions
```typescript
// Page assertions
await expect(page).toHaveTitle(/JobFinder/);
await expect(page).toHaveURL(/.*dashboard/);

// Element assertions
await expect(page.locator('.success')).toBeVisible();
await expect(page.locator('h1')).toHaveText('Welcome');
await expect(page.locator('.error')).toBeHidden();
await expect(page.locator('input')).toHaveValue('test');
await expect(page.locator('button')).toBeEnabled();
await expect(page.locator('.loading')).toBeDisabled();

// Count assertions
await expect(page.locator('.item')).toHaveCount(5);
```

## MCP Browser Tools (Warp AI)

### Navigation
```
browser_navigate         - Go to URL
browser_navigate_back    - Go back
browser_close           - Close page
```

### Interaction
```
browser_click           - Click element
browser_type            - Type text
browser_hover           - Hover element
browser_press_key       - Press key
browser_drag            - Drag and drop
browser_select_option   - Select dropdown
browser_fill_form       - Fill multiple fields
```

### Information
```
browser_snapshot        - Get page structure (best for AI)
browser_take_screenshot - Take screenshot
browser_console_messages - Get console logs
browser_network_requests - Get network activity
```

### Advanced
```
browser_evaluate        - Run JavaScript
browser_run_code        - Run Playwright code
browser_wait_for        - Wait for condition
browser_handle_dialog   - Handle alert/confirm
browser_file_upload     - Upload file
browser_tabs            - Manage tabs
browser_resize          - Change viewport
```

## Example MCP Conversations

```
You: "Navigate to localhost:3000 and take a screenshot"
You: "Click the login button and fill in the form"
You: "Test the mobile responsiveness at 375px width"
You: "Check if there are console errors on the homepage"
You: "Fill the signup form with test@example.com and password123"
```

## Debugging

```powershell
# Debug mode (recommended)
npx playwright test --debug

# Generate test code
npx playwright codegen localhost:3000

# Inspector
npx playwright inspector

# Trace viewer (after test run)
npx playwright show-trace trace.zip
```

## Useful Flags

```powershell
--headed              # Show browser
--debug              # Debug mode
--ui                 # UI mode
--project=chromium   # Specific browser
--grep="login"       # Run matching tests
--workers=1          # Sequential execution
--retries=2          # Retry failed tests
```

## File Locations

```
E:\JobFinder\
├── playwright.config.ts          # Main config
├── mcp-playwright-server.json    # MCP config
├── .env.test.example             # Environment template
├── tests/
│   └── e2e/
│       ├── homepage.spec.ts      # Homepage tests
│       ├── auth.spec.ts          # Auth tests
│       └── fixtures.ts           # Utilities
├── test-results/                 # Test output
├── playwright-report/            # HTML reports
├── scripts/
│   └── setup-playwright.ps1      # Setup script
└── docs/
    ├── PLAYWRIGHT_MCP_SETUP.md   # Full guide
    └── PLAYWRIGHT_QUICK_REFERENCE.md  # This file
```

## Environment Variables

```bash
# .env.test
BASE_URL=http://localhost:3000
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123
API_BASE_URL=http://localhost:5000/api
```

## Best Practices Checklist

- ✓ Use descriptive test names
- ✓ Prefer accessibility selectors (`getByRole`, `getByLabel`)
- ✓ Wait for network requests before assertions
- ✓ Use `test.beforeEach` for setup
- ✓ Keep tests independent
- ✓ Use Page Object Model for complex pages
- ✓ Take screenshots on failure (automatic)
- ✓ Use fixtures for reusable setup
- ✓ Run tests in UI mode during development
- ✓ Use `--debug` when tests fail

## Common Issues

**Tests timeout:**
- Increase timeout in config
- Wait for network idle
- Check if app is running

**Can't find element:**
- Use `--debug` mode
- Use `codegen` to generate selectors
- Check if element is loaded

**Browser not launching:**
- Run `npx playwright install`
- Check browser installation

**Port in use:**
- Check if app is running
- Change BASE_URL in config

## Next Steps

1. Run setup: `.\scripts\setup-playwright.ps1`
2. Copy `.env.test.example` to `.env.test`
3. Start dev server: `npm run dev:frontend`
4. Run tests: `npm run test:e2e:ui`
5. Try MCP: Ask Warp AI to test your app!

## Resources

- [Full Documentation](./PLAYWRIGHT_MCP_SETUP.md)
- [Playwright Docs](https://playwright.dev)
- [Tests README](../tests/README.md)
- [MCP Protocol](https://modelcontextprotocol.io)
