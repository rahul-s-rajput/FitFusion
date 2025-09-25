/**
 * PWA Installation Flow Integration Tests
 * These tests verify PWA functionality and will fail until implementation is complete.
 */

import { test, expect } from '@playwright/test';

test.describe('PWA Installation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
  });

  test('should have PWA manifest', async ({ page }) => {
    // Check that manifest is linked in HTML
    const manifestLink = page.locator('link[rel="manifest"]');
    await expect(manifestLink).toBeAttached();
    
    const manifestHref = await manifestLink.getAttribute('href');
    expect(manifestHref).toBe('/manifest.json');
  });

  test('should have service worker registration', async ({ page }) => {
    // Check that service worker is registered
    const swRegistered = await page.evaluate(async () => {
      if ('serviceWorker' in navigator) {
        try {
          const registration = await navigator.serviceWorker.getRegistration();
          return !!registration;
        } catch (error) {
          return false;
        }
      }
      return false;
    });
    
    expect(swRegistered).toBe(true);
  });

  test('should show install prompt on supported browsers', async ({ page, browserName }) => {
    // Skip on browsers that don't support PWA installation
    test.skip(browserName === 'firefox', 'Firefox does not support PWA installation');
    
    // Simulate beforeinstallprompt event
    await page.evaluate(() => {
      const event = new Event('beforeinstallprompt');
      window.dispatchEvent(event);
    });
    
    // Check if install button or prompt appears
    const installButton = page.locator('[data-testid="install-pwa-button"]');
    await expect(installButton).toBeVisible({ timeout: 5000 });
  });

  test('should handle install button click', async ({ page, browserName }) => {
    test.skip(browserName === 'firefox', 'Firefox does not support PWA installation');
    
    // Mock the beforeinstallprompt event
    await page.addInitScript(() => {
      let deferredPrompt: any;
      
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Mock prompt method
        deferredPrompt.prompt = () => Promise.resolve();
        deferredPrompt.userChoice = Promise.resolve({ outcome: 'accepted' });
        
        // Dispatch custom event to show install button
        window.dispatchEvent(new CustomEvent('pwa-installable'));
      });
      
      // Trigger the event immediately
      setTimeout(() => {
        const event = new Event('beforeinstallprompt') as any;
        event.preventDefault = () => {};
        window.dispatchEvent(event);
      }, 100);
    });
    
    // Wait for install button to appear
    const installButton = page.locator('[data-testid="install-pwa-button"]');
    await expect(installButton).toBeVisible({ timeout: 10000 });
    
    // Click install button
    await installButton.click();
    
    // Verify install process was initiated
    // (In a real test, you'd check for success message or UI changes)
    await expect(page.locator('[data-testid="install-success-message"]')).toBeVisible({ timeout: 5000 });
  });

  test('should work offline after installation', async ({ page }) => {
    // First, load the page online to cache resources
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
    
    // Go offline
    await page.context().setOffline(true);
    
    // Reload the page
    await page.reload();
    
    // Should still work offline
    await expect(page.locator('h1')).toBeVisible();
    
    // Should show offline indicator
    const offlineIndicator = page.locator('[data-testid="offline-indicator"]');
    await expect(offlineIndicator).toBeVisible({ timeout: 5000 });
  });

  test('should cache API responses for offline use', async ({ page }) => {
    // Load page and make API calls
    await page.goto('/');
    
    // Navigate to equipment page to trigger API calls
    await page.click('[data-testid="equipment-nav-link"]');
    await expect(page.locator('[data-testid="equipment-list"]')).toBeVisible();
    
    // Go offline
    await page.context().setOffline(true);
    
    // Reload equipment page
    await page.reload();
    
    // Should still show cached equipment data
    await expect(page.locator('[data-testid="equipment-list"]')).toBeVisible();
    
    // Should show offline message for new data
    const offlineMessage = page.locator('[data-testid="offline-data-message"]');
    await expect(offlineMessage).toBeVisible();
  });

  test('should sync data when coming back online', async ({ page }) => {
    // Start offline
    await page.context().setOffline(true);
    await page.goto('/');
    
    // Add equipment while offline
    await page.click('[data-testid="add-equipment-button"]');
    await page.fill('[data-testid="equipment-name-input"]', 'Offline Dumbbells');
    await page.selectOption('[data-testid="equipment-category-select"]', 'weights');
    await page.click('[data-testid="save-equipment-button"]');
    
    // Should show pending sync indicator
    const pendingSync = page.locator('[data-testid="pending-sync-indicator"]');
    await expect(pendingSync).toBeVisible();
    
    // Go back online
    await page.context().setOffline(false);
    
    // Should automatically sync and remove pending indicator
    await expect(pendingSync).toBeHidden({ timeout: 10000 });
    
    // Should show sync success message
    const syncSuccess = page.locator('[data-testid="sync-success-message"]');
    await expect(syncSuccess).toBeVisible({ timeout: 5000 });
  });

  test('should handle PWA shortcuts', async ({ page }) => {
    // Check that shortcuts are defined in manifest
    const shortcuts = await page.evaluate(async () => {
      const response = await fetch('/manifest.json');
      const manifest = await response.json();
      return manifest.shortcuts;
    });
    
    expect(shortcuts).toBeDefined();
    expect(shortcuts.length).toBeGreaterThan(0);
    
    // Verify shortcut structure
    const workoutShortcut = shortcuts.find((s: any) => s.name.includes('Workout'));
    expect(workoutShortcut).toBeDefined();
    expect(workoutShortcut.url).toBeDefined();
    expect(workoutShortcut.icons).toBeDefined();
  });

  test('should display correctly in standalone mode', async ({ page }) => {
    // Simulate standalone display mode
    await page.addInitScript(() => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: (query: string) => ({
          matches: query === '(display-mode: standalone)',
          media: query,
          onchange: null,
          addListener: () => {},
          removeListener: () => {},
          addEventListener: () => {},
          removeEventListener: () => {},
          dispatchEvent: () => {},
        }),
      });
    });
    
    await page.goto('/');
    
    // Should hide browser UI elements when in standalone mode
    const browserChrome = page.locator('[data-testid="browser-chrome"]');
    await expect(browserChrome).toBeHidden();
    
    // Should show app-specific navigation
    const appNavigation = page.locator('[data-testid="app-navigation"]');
    await expect(appNavigation).toBeVisible();
  });

  test('should handle app updates gracefully', async ({ page }) => {
    // Load initial version
    await page.goto('/');
    
    // Simulate service worker update
    await page.evaluate(() => {
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          // Dispatch custom event for app update
          window.dispatchEvent(new CustomEvent('app-update-available'));
        });
        
        // Simulate update
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('app-update-available'));
        }, 1000);
      }
    });
    
    // Should show update notification
    const updateNotification = page.locator('[data-testid="app-update-notification"]');
    await expect(updateNotification).toBeVisible({ timeout: 5000 });
    
    // Should have reload button
    const reloadButton = page.locator('[data-testid="reload-app-button"]');
    await expect(reloadButton).toBeVisible();
    
    // Click reload should refresh the app
    await reloadButton.click();
    await expect(page.locator('h1')).toBeVisible();
  });
});
