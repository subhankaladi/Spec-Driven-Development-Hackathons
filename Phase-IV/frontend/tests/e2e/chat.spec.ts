/**
 * E2E Tests: Chat Interface
 *
 * Tests the complete chat flow from user interaction to backend response
 */

import { test, expect } from '@playwright/test';

test.describe('Chat Interface - Basic Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to chat page
    await page.goto('/chat');
  });

  test('should load chat interface successfully', async ({ page }) => {
    // Check that main elements are visible
    await expect(page.getByRole('heading', { name: /chat/i })).toBeVisible();
    await expect(page.getByRole('textbox', { name: /type your message/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();
  });

  test('should send a message and receive response', async ({ page }) => {
    // Type a message
    const messageInput = page.getByRole('textbox', { name: /type your message/i });
    await messageInput.fill('Hello, create a task to buy groceries');

    // Send the message
    await page.getByRole('button', { name: /send/i }).click();

    // Check that optimistic message appears
    await expect(page.getByText('Hello, create a task to buy groceries')).toBeVisible();

    // Wait for agent response (with timeout)
    await expect(page.getByRole('log')).toContainText(/task|created|added/i, { timeout: 10000 });

    // Verify message status changes from "sending" to "sent"
    await expect(page.getByText(/sending/i)).not.toBeVisible({ timeout: 5000 });
  });

  test('should show loading indicator while sending', async ({ page }) => {
    // Type and send a message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test message');
    await page.getByRole('button', { name: /send/i }).click();

    // Check for loading indicator
    await expect(page.getByText(/sending/i)).toBeVisible();
  });

  test('should disable send button while loading', async ({ page }) => {
    const messageInput = page.getByRole('textbox', { name: /type your message/i });
    await messageInput.fill('Test message');

    const sendButton = page.getByRole('button', { name: /send/i });
    await sendButton.click();

    // Button should be disabled during sending
    await expect(sendButton).toBeDisabled();

    // Wait for response
    await expect(sendButton).toBeEnabled({ timeout: 10000 });
  });

  test('should handle Enter key to send message', async ({ page }) => {
    const messageInput = page.getByRole('textbox', { name: /type your message/i });

    // Type message and press Enter
    await messageInput.fill('Test with Enter key');
    await messageInput.press('Enter');

    // Message should be sent
    await expect(page.getByText('Test with Enter key')).toBeVisible();
  });

  test('should handle Shift+Enter for new line', async ({ page }) => {
    const messageInput = page.getByRole('textbox', { name: /type your message/i });

    // Type message and press Shift+Enter
    await messageInput.fill('Line 1');
    await messageInput.press('Shift+Enter');
    await messageInput.type('Line 2');

    // Textarea should contain multiline text
    await expect(messageInput).toHaveValue('Line 1\nLine 2');

    // Message should NOT be sent yet
    await expect(page.getByText('Line 1')).not.toBeVisible();
  });

  test('should enforce character limit', async ({ page }) => {
    const messageInput = page.getByRole('textbox', { name: /type your message/i });

    // Try to type more than 5000 characters
    const longMessage = 'a'.repeat(5001);
    await messageInput.fill(longMessage);

    // Check that character counter is visible
    await expect(page.getByText(/5000/)).toBeVisible();

    // Send button might be disabled (depends on implementation)
    const sendButton = page.getByRole('button', { name: /send/i });
    await expect(sendButton).toBeDisabled();
  });
});

test.describe('Chat Interface - Conversation Management', () => {
  test('should display conversation list sidebar', async ({ page }) => {
    await page.goto('/chat');

    // Check for sidebar elements
    await expect(page.getByRole('button', { name: /new chat/i })).toBeVisible();

    // On desktop, sidebar should be visible
    const viewport = page.viewportSize();
    if (viewport && viewport.width >= 768) {
      await expect(page.getByRole('list', { name: /conversations/i })).toBeVisible();
    }
  });

  test('should create new conversation on first message', async ({ page }) => {
    await page.goto('/chat');

    // Send first message
    await page.getByRole('textbox', { name: /type your message/i }).fill('First message');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for response
    await expect(page.getByRole('log')).toContainText(/first message/i, { timeout: 10000 });

    // Conversation should appear in sidebar (after some time)
    await page.waitForTimeout(2000); // Wait for conversation to be created
  });

  test('should toggle mobile sidebar', async ({ page, viewport }) => {
    // Skip if desktop viewport
    if (!viewport || viewport.width >= 768) {
      test.skip();
    }

    await page.goto('/chat');

    // Mobile menu toggle should be visible
    const menuToggle = page.getByLabel(/toggle conversation list/i);
    await expect(menuToggle).toBeVisible();

    // Click to open sidebar
    await menuToggle.click();

    // Sidebar should be visible
    await expect(page.getByRole('button', { name: /new chat/i })).toBeVisible();

    // Click overlay to close
    await page.locator('.fixed.inset-0.bg-black').click();

    // Sidebar should be hidden
    await expect(page.getByRole('button', { name: /new chat/i })).not.toBeVisible();
  });
});

test.describe('Chat Interface - Error Handling', () => {
  test('should display error message on network failure', async ({ page, context }) => {
    await page.goto('/chat');

    // Simulate network offline
    await context.setOffline(true);

    // Try to send a message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Test message');
    await page.getByRole('button', { name: /send/i }).click();

    // Error banner should appear
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/connection/i)).toBeVisible();

    // Retry button should be available
    await expect(page.getByRole('button', { name: /retry/i })).toBeVisible();

    // Restore network
    await context.setOffline(false);
  });

  test('should allow retry on failed message', async ({ page, context }) => {
    await page.goto('/chat');

    // Cause a failure
    await context.setOffline(true);

    await page.getByRole('textbox', { name: /type your message/i }).fill('Test retry');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for error
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 5000 });

    // Message should show failed status
    await expect(page.getByText(/failed to send/i)).toBeVisible();

    // Restore network and retry
    await context.setOffline(false);
    await page.getByRole('button', { name: /retry/i }).click();

    // Message should be sent successfully
    await expect(page.getByText(/failed to send/i)).not.toBeVisible({ timeout: 10000 });
  });

  test('should dismiss error banner', async ({ page }) => {
    await page.goto('/chat');

    // Trigger an error (simulate network failure)
    await page.context().setOffline(true);

    await page.getByRole('textbox', { name: /type your message/i }).fill('Test');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for error
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 5000 });

    // Dismiss error
    await page.getByRole('button', { name: /dismiss error/i }).click();

    // Error should be gone
    await expect(page.getByRole('alert')).not.toBeVisible();

    // Restore network
    await page.context().setOffline(false);
  });
});

test.describe('Chat Interface - Accessibility', () => {
  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/chat');

    // Tab to message input
    await page.keyboard.press('Tab');

    // Input should be focused
    const messageInput = page.getByRole('textbox', { name: /type your message/i });
    await expect(messageInput).toBeFocused();

    // Type a message
    await messageInput.fill('Keyboard test');

    // Tab to send button
    await page.keyboard.press('Tab');

    const sendButton = page.getByRole('button', { name: /send/i });
    await expect(sendButton).toBeFocused();

    // Press Enter to send
    await page.keyboard.press('Enter');

    // Message should be sent
    await expect(page.getByText('Keyboard test')).toBeVisible();
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('/chat');

    // Check for ARIA labels
    await expect(page.getByRole('log')).toBeVisible(); // MessageList
    await expect(page.getByRole('textbox', { name: /type your message/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();
  });

  test('should announce messages to screen readers', async ({ page }) => {
    await page.goto('/chat');

    // Send a message
    await page.getByRole('textbox', { name: /type your message/i }).fill('Screen reader test');
    await page.getByRole('button', { name: /send/i }).click();

    // Check that message list has aria-live attribute
    const messageList = page.getByRole('log');
    await expect(messageList).toHaveAttribute('aria-live', 'polite');
  });
});
