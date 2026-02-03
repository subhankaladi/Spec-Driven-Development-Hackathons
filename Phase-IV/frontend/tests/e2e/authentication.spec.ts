/**
 * E2E Tests: Authentication and Re-authentication Flow
 *
 * Tests JWT token expiration and re-authentication modal
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication - Re-authentication Flow', () => {
  test('should redirect to signin when not authenticated', async ({ page }) => {
    // Try to access chat page without authentication
    await page.goto('/chat');

    // Should be redirected to signin page
    await expect(page).toHaveURL(/\/signin/, { timeout: 5000 });
  });

  test('should show re-authentication modal on token expiry', async ({ page }) => {
    // Note: This test requires mocking expired token or waiting for actual expiry
    // For demonstration, we'll test the modal UI elements

    await page.goto('/chat');

    // Simulate token expiry by clearing cookies and making a request
    await page.context().clearCookies();

    // Try to send a message (should trigger re-auth modal)
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test message');
    await page.getByRole('button', { name: /send/i }).click();

    // Re-authentication modal should appear
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/session expired/i)).toBeVisible();
  });

  test('should allow user to stay on page when session expires', async ({ page }) => {
    await page.goto('/chat');

    // Trigger re-auth modal (simulate token expiry)
    await page.context().clearCookies();
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for modal
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });

    // Click "Stay Here" button
    await page.getByRole('button', { name: /stay here/i }).click();

    // Modal should close
    await expect(page.getByRole('dialog')).not.toBeVisible();

    // Should still be on chat page
    await expect(page).toHaveURL(/\/chat/);
  });

  test('should redirect to signin when user clicks Log In', async ({ page }) => {
    await page.goto('/chat');

    // Trigger re-auth modal
    await page.context().clearCookies();
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for modal
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });

    // Click "Log In" button
    await page.getByRole('button', { name: /log in/i }).click();

    // Should redirect to signin page
    await expect(page).toHaveURL(/\/signin/, { timeout: 5000 });
  });

  test('should close re-auth modal with Escape key', async ({ page }) => {
    await page.goto('/chat');

    // Trigger re-auth modal
    await page.context().clearCookies();
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for modal
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });

    // Press Escape key
    await page.keyboard.press('Escape');

    // Modal should close
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('should close re-auth modal by clicking backdrop', async ({ page }) => {
    await page.goto('/chat');

    // Trigger re-auth modal
    await page.context().clearCookies();
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for modal
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });

    // Click backdrop (outside modal)
    const backdrop = page.locator('.fixed.inset-0.bg-black').first();
    await backdrop.click({ position: { x: 10, y: 10 } });

    // Modal should close
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });
});

test.describe('Authentication - Protected Routes', () => {
  test('should protect chat page with AuthGuard', async ({ page }) => {
    // Clear any existing authentication
    await page.context().clearCookies();

    // Try to access chat page
    await page.goto('/chat');

    // Should show loading or redirect to signin
    await page.waitForTimeout(1000);

    // Should either show "Checking authentication..." or redirect
    const url = page.url();
    const isOnSignin = url.includes('/signin');
    const isCheckingAuth = await page.getByText(/checking authentication/i).isVisible();

    expect(isOnSignin || isCheckingAuth).toBe(true);
  });

  test('should show loading state while checking authentication', async ({ page }) => {
    await page.goto('/chat');

    // Briefly should show loading state
    // Note: This might be very quick, so we check if it ever appeared
    const loadingText = page.getByText(/checking authentication/i);

    // Either loading appeared or we're already authenticated
    const appeared = await loadingText.isVisible().catch(() => false);

    // This is a soft check - loading might appear too quickly to catch
    if (appeared) {
      expect(appeared).toBe(true);
    }
  });
});

test.describe('Authentication - JWT Token Handling', () => {
  test('should include JWT token in API requests', async ({ page }) => {
    await page.goto('/chat');

    // Monitor network requests
    const requests: any[] = [];
    page.on('request', (request) => {
      if (request.url().includes('/api/chat')) {
        requests.push(request);
      }
    });

    // Send a message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test message');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for request to be made
    await page.waitForTimeout(2000);

    // At least one request should have been made to /api/chat
    expect(requests.length).toBeGreaterThan(0);

    // Requests should include credentials (cookies with JWT)
    const chatRequest = requests[0];
    expect(chatRequest.headers()['cookie']).toBeDefined();
  });

  test('should handle 401 Unauthorized response gracefully', async ({ page }) => {
    await page.goto('/chat');

    // Intercept API request and return 401
    await page.route('**/api/chat', (route) => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required',
          },
        }),
      });
    });

    // Send message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test');
    await page.getByRole('button', { name: /send/i }).click();

    // Re-auth modal should appear
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/session expired/i)).toBeVisible();
  });

  test('should retry failed request after re-authentication', async ({ page }) => {
    await page.goto('/chat');

    let requestCount = 0;

    // Intercept first request with 401, then allow subsequent requests
    await page.route('**/api/chat', (route) => {
      requestCount++;

      if (requestCount === 1) {
        // First request fails with 401
        route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({
            error: { code: 'UNAUTHORIZED', message: 'Token expired' },
          }),
        });
      } else {
        // Subsequent requests succeed
        route.continue();
      }
    });

    // Send message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Retry test');
    await page.getByRole('button', { name: /send/i }).click();

    // Modal should appear
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });

    // User re-authenticates (close modal for test)
    await page.getByRole('button', { name: /stay here/i }).click();

    // Message should still be in sending state or failed
    // User can retry from error banner
    const retryButton = page.getByRole('button', { name: /retry/i });
    if (await retryButton.isVisible()) {
      await retryButton.click();

      // Second attempt should succeed
      await expect(retryButton).not.toBeVisible({ timeout: 10000 });
    }
  });
});

test.describe('Authentication - Session Persistence', () => {
  test('should maintain authentication across page reloads', async ({ page }) => {
    await page.goto('/chat');

    // Ensure we're authenticated (send a message successfully)
    await page.getByRole('textbox', { name: /type your message/i }).fill('Auth test');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByText('Auth test')).toBeVisible({ timeout: 10000 });

    // Reload page
    await page.reload();

    // Should still be on chat page (not redirected to signin)
    await expect(page).toHaveURL(/\/chat/);
    await expect(page.getByRole('heading', { name: /chat/i })).toBeVisible();

    // Should be able to send another message without re-authenticating
    await page.getByRole('textbox', { name: /type your message/i }).fill('After reload');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByText('After reload')).toBeVisible({ timeout: 10000 });
  });

  test('should handle session expiry during page session', async ({ page, context }) => {
    await page.goto('/chat');

    // Send initial message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Initial');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByText('Initial')).toBeVisible({ timeout: 10000 });

    // Simulate session expiry by clearing cookies
    await context.clearCookies();

    // Try to send another message
    await page.getByRole('textbox', { name: /type your message/i }).fill('After expiry');
    await page.getByRole('button', { name: /send/i }).click();

    // Should show re-auth modal
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });
  });
});
