# Playwright MCP Setup for JobFinder

This document explains how to set up and use Playwright with MCP (Model Context Protocol) integration for E2E testing in the JobFinder project.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [MCP Integration](#mcp-integration)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [MCP Browser Tools](#mcp-browser-tools)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Installation

### 1. Install Playwright and Dependencies

```powershell
# From project root (E:\JobFinder)
npm install -D @playwright/test
npx playwright install
```

### 2. Install Playwright Browsers

```powershell
npx playwright install chromium firefox webkit
```

### 3. Install MCP Playwright Server (Optional for MCP integration)

```powershell
npm install -g @executeautomation/playwright-mcp-server
```

## Configuration

### Playwright Config
The main configuration file is `playwright.config.ts` in the project root. It includes:

- Multiple browser configurations (Chromium, Firefox, WebKit, Mobile)
- Automatic dev server startup
- Screenshot and video capture on failures
- Trace collection for debugging
- HTML and JSON reporters

### Environment Variables
Copy `.env.test.example` to `.env.test` and configure:

```bash
BASE_URL=http://localhost:3000
TEST_USER_EMAIL=your-test-email@example.com
TEST_USER_PASSWORD=your-test-password
```

## MCP Integration

### What is MCP?
Model Context Protocol (MCP) allows AI assistants (like Claude, Warp AI) to control and interact with Playwright browsers directly through standardized tools.

### MCP Server Configuration
The `mcp-playwright-server.json` file configures the MCP server:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"],
      "env": {
        "PLAYWRIGHT_BASE_URL": "http://localhost:3000",
        "PLAYWRIGHT_HEADLESS": "false",
        "PLAYWRIGHT_TIMEOUT": "30000",
        "PLAYWRIGHT_BROWSER": "chromium"
      }
    }
  }
}
```

### Using MCP in Warp
Since you're using Warp with MCP support, you can now use browser automation tools directly in your AI conversations:

1. **browser_navigate** - Navigate to URLs
2. **browser_click** - Click elements
3. **browser_type** - Type text into inputs
4. **browser_snapshot** - Capture page state
5. **browser_take_screenshot** - Take screenshots
6. And many more (see MCP Browser Tools section)

Example interaction:
```
You: "Navigate to http://localhost:3000 and take a screenshot"
AI: [Uses browser_navigate and browser_take_screenshot MCP tools]
```

## Running Tests

### Run All Tests
```powershell
npx playwright test
```

### Run Specific Test File
```powershell
npx playwright test tests/e2e/homepage.spec.ts
```

### Run Tests in UI Mode (Interactive)
```powershell
npx playwright test --ui
```

### Run Tests in Headed Mode (Watch Browser)
```powershell
npx playwright test --headed
```

### Run Tests on Specific Browser
```powershell
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Debug Tests
```powershell
npx playwright test --debug
```

### View Test Report
```powershell
npx playwright show-report
```

## Writing Tests

### Basic Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Expected Title/);
  });
});
```

### Using Custom Fixtures
```typescript
import { test, expect } from '../fixtures';

test('should access authenticated page', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/dashboard');
  await expect(authenticatedPage).toHaveURL(/.*dashboard/);
});
```

### Common Patterns

#### Waiting for Elements
```typescript
await page.waitForSelector('.loading-spinner', { state: 'hidden' });
await page.waitForLoadState('networkidle');
```

#### Interacting with Forms
```typescript
await page.fill('input[name="email"]', 'test@example.com');
await page.fill('input[name="password"]', 'password123');
await page.click('button[type="submit"]');
```

#### Assertions
```typescript
await expect(page.locator('.success-message')).toBeVisible();
await expect(page).toHaveURL(/.*dashboard/);
await expect(page.locator('h1')).toHaveText('Welcome');
```

## MCP Browser Tools

Available MCP tools for browser automation (accessible through Warp AI):

### Navigation Tools
- **browser_navigate** - Navigate to a URL
- **browser_navigate_back** - Go back to previous page
- **browser_close** - Close the page

### Interaction Tools
- **browser_click** - Click on elements
- **browser_type** - Type text into inputs
- **browser_hover** - Hover over elements
- **browser_press_key** - Press keyboard keys
- **browser_drag** - Drag and drop elements
- **browser_select_option** - Select dropdown options
- **browser_fill_form** - Fill multiple form fields

### Information Tools
- **browser_snapshot** - Capture accessibility snapshot (better than screenshot for AI)
- **browser_take_screenshot** - Take visual screenshot
- **browser_console_messages** - Get console logs
- **browser_network_requests** - Get network activity

### Advanced Tools
- **browser_evaluate** - Run JavaScript on page
- **browser_run_code** - Run Playwright code snippets
- **browser_wait_for** - Wait for conditions
- **browser_handle_dialog** - Handle alerts/confirms
- **browser_file_upload** - Upload files
- **browser_tabs** - Manage browser tabs

### Example MCP Usage

You can ask Warp AI to:
- "Navigate to localhost:3000 and click the login button"
- "Fill out the signup form with test data"
- "Take a screenshot of the dashboard"
- "Check if there are any console errors on the homepage"
- "Test the mobile responsiveness of the landing page"

## Best Practices

### 1. Use Page Object Model
```typescript
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}
  
  async login(email: string, password: string) {
    await this.page.fill('[name="email"]', email);
    await this.page.fill('[name="password"]', password);
    await this.page.click('button[type="submit"]');
  }
}
```

### 2. Use Test Fixtures
- Create reusable fixtures for common setup
- Use `authenticatedPage` fixture for protected routes
- Add custom fixtures in `fixtures.ts`

### 3. Wait for Network Requests
```typescript
await page.waitForResponse(response => 
  response.url().includes('/api/user') && response.status() === 200
);
```

### 4. Use Accessibility Selectors
```typescript
// Prefer role-based selectors
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByLabel('Email').fill('test@example.com');
```

### 5. Parallel Test Execution
- Tests run in parallel by default
- Use `test.describe.serial()` for sequential tests
- Use `test.beforeEach()` for test isolation

## Troubleshooting

### Browser Not Installed
```powershell
npx playwright install chromium
```

### Tests Failing Due to Timeouts
- Increase timeout in `playwright.config.ts`
- Use `await page.waitForLoadState('networkidle')`
- Check if dev server is running

### Port Already in Use
- Check if frontend is already running on port 3000
- Change `BASE_URL` in config if using different port

### MCP Server Not Responding
```powershell
# Reinstall MCP server
npm install -g @executeautomation/playwright-mcp-server

# Check MCP server status in Warp settings
```

### Screenshots Not Saving
```powershell
# Create directories
New-Item -ItemType Directory -Force -Path test-results/screenshots
```

## Additional Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Warp MCP Integration](https://docs.warp.dev/features/mcp)

## Next Steps

1. Install Playwright: `npm install -D @playwright/test`
2. Install browsers: `npx playwright install`
3. Copy `.env.test.example` to `.env.test`
4. Run sample tests: `npx playwright test`
5. View report: `npx playwright show-report`
6. Try MCP integration: Ask Warp AI to navigate and test your app!

## Support

For issues or questions:
- Check the [Playwright Discord](https://discord.gg/playwright)
- Review test logs in `test-results/`
- Use `--debug` flag for step-by-step debugging
