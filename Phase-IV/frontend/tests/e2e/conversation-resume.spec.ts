/**
 * E2E Tests: Conversation Resume
 *
 * Tests that conversations persist after page refresh
 */

import { test, expect } from '@playwright/test';

test.describe('Conversation Resume - Page Refresh', () => {
  test('should persist conversation after page refresh', async ({ page }) => {
    await page.goto('/chat');

    // Send first message to create conversation
    const messageInput = page.getByRole('textbox', { name: /type your message/i });
    await messageInput.fill('Create a task to buy milk');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for response
    await expect(page.getByRole('log')).toContainText(/buy milk/i, { timeout: 10000 });
    await expect(page.getByRole('log')).toContainText(/task|created/i, { timeout: 10000 });

    // Get the number of messages before refresh
    const messages = page.getByRole('log').locator('[role="article"]');
    const initialCount = await messages.count();

    // Refresh the page
    await page.reload();

    // Wait for page to load
    await expect(page.getByRole('heading', { name: /chat/i })).toBeVisible();

    // Messages should still be visible
    await expect(page.getByText('Create a task to buy milk')).toBeVisible({ timeout: 5000 });

    // Message count should be the same or greater
    const messagesAfterRefresh = page.getByRole('log').locator('[role="article"]');
    const countAfterRefresh = await messagesAfterRefresh.count();

    expect(countAfterRefresh).toBeGreaterThanOrEqual(initialCount);
  });

  test('should load conversation history from sidebar', async ({ page }) => {
    await page.goto('/chat');

    // Send a message to create first conversation
    await page.getByRole('textbox', { name: /type your message/i }).fill('First conversation message');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByRole('log')).toContainText(/first conversation/i, { timeout: 10000 });

    // Start new conversation
    await page.getByRole('button', { name: /new chat/i }).click();

    // Send message in new conversation
    await page.getByRole('textbox', { name: /type your message/i }).fill('Second conversation message');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByRole('log')).toContainText(/second conversation/i, { timeout: 10000 });

    // Wait for conversations to appear in sidebar
    await page.waitForTimeout(2000);

    // Go back to first conversation (click on it in sidebar)
    const conversationList = page.getByRole('list', { name: /conversations/i });
    if (await conversationList.isVisible()) {
      const firstConv = conversationList.locator('button').first();
      await firstConv.click();

      // First conversation messages should be visible
      await expect(page.getByText('First conversation message')).toBeVisible({ timeout: 5000 });

      // Second conversation message should NOT be visible
      await expect(page.getByText('Second conversation message')).not.toBeVisible();
    }
  });

  test('should continue existing conversation with new message', async ({ page }) => {
    await page.goto('/chat');

    // Send first message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Initial message');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByRole('log')).toContainText(/initial message/i, { timeout: 10000 });

    // Refresh page
    await page.reload();

    // Wait for conversation to load
    await expect(page.getByText('Initial message')).toBeVisible({ timeout: 5000 });

    // Send follow-up message in same conversation
    await page.getByRole('textbox', { name: /type your message/i }).fill('Follow-up message');
    await page.getByRole('button', { name: /send/i }).click();

    // Both messages should be visible
    await expect(page.getByText('Initial message')).toBeVisible();
    await expect(page.getByText('Follow-up message')).toBeVisible();

    // Should show at least 3 messages (initial user + agent + follow-up user + agent)
    const messages = page.getByRole('log').locator('[role="article"]');
    const count = await messages.count();
    expect(count).toBeGreaterThanOrEqual(3);
  });

  test('should show conversation list with titles', async ({ page }) => {
    await page.goto('/chat');

    // Send message to create conversation
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test conversation title');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByRole('log')).toContainText(/test conversation/i, { timeout: 10000 });

    // Wait for conversation to appear in sidebar
    await page.waitForTimeout(2000);

    // Refresh to ensure conversation persists
    await page.reload();

    // Conversation should appear in sidebar with a title
    const conversationList = page.getByRole('list', { name: /conversations/i });

    // On desktop, check if conversation list is visible
    const viewport = page.viewportSize();
    if (viewport && viewport.width >= 768) {
      await expect(conversationList).toBeVisible();

      // At least one conversation item should exist
      const conversationItems = conversationList.locator('button');
      await expect(conversationItems.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('should preserve message timestamps after refresh', async ({ page }) => {
    await page.goto('/chat');

    // Send message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Timestamp test');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByRole('log')).toContainText(/timestamp test/i, { timeout: 10000 });

    // Get timestamp before refresh
    const timestampBefore = await page.locator('text=/\\d{1,2}:\\d{2}/').first().textContent();

    // Refresh page
    await page.reload();

    // Wait for messages to load
    await expect(page.getByText('Timestamp test')).toBeVisible({ timeout: 5000 });

    // Get timestamp after refresh
    const timestampAfter = await page.locator('text=/\\d{1,2}:\\d{2}/').first().textContent();

    // Timestamps should match (or be very close)
    expect(timestampAfter).toBe(timestampBefore);
  });
});

test.describe('Conversation Resume - Multiple Conversations', () => {
  test('should handle switching between multiple conversations', async ({ page }) => {
    await page.goto('/chat');

    // Create first conversation
    await page.getByRole('textbox', { name: /type your message/i }).fill('Conversation 1 message');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByRole('log')).toContainText(/conversation 1/i, { timeout: 10000 });

    // Create second conversation
    await page.getByRole('button', { name: /new chat/i }).click();
    await page.getByRole('textbox', { name: /type your message/i }).fill('Conversation 2 message');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByRole('log')).toContainText(/conversation 2/i, { timeout: 10000 });

    // Wait for sidebar to update
    await page.waitForTimeout(2000);

    // Verify we can switch between conversations
    const viewport = page.viewportSize();
    if (viewport && viewport.width >= 768) {
      const conversationList = page.getByRole('list', { name: /conversations/i });
      const conversations = conversationList.locator('button');

      // Should have at least 2 conversations
      await expect(conversations).toHaveCount(2, { timeout: 5000 });

      // Click on first conversation
      await conversations.nth(0).click();

      // Should show first conversation messages
      await expect(page.getByText('Conversation 1 message')).toBeVisible({ timeout: 3000 });

      // Click on second conversation
      await conversations.nth(1).click();

      // Should show second conversation messages
      await expect(page.getByText('Conversation 2 message')).toBeVisible({ timeout: 3000 });
    }
  });

  test('should clear messages when starting new conversation', async ({ page }) => {
    await page.goto('/chat');

    // Send message in first conversation
    await page.getByRole('textbox', { name: /type your message/i }).fill('Old message');
    await page.getByRole('button', { name: /send/i }).click();

    await expect(page.getByText('Old message')).toBeVisible({ timeout: 10000 });

    // Start new conversation
    await page.getByRole('button', { name: /new chat/i }).click();

    // Old message should not be visible
    await expect(page.getByText('Old message')).not.toBeVisible();

    // Message input should be empty
    const messageInput = page.getByRole('textbox', { name: /type your message/i });
    await expect(messageInput).toHaveValue('');

    // Message list should be empty (or show welcome message)
    const messages = page.getByRole('log').locator('[role="article"]');
    const count = await messages.count();
    expect(count).toBe(0);
  });
});
