/**
 * Equipment Management Integration Tests
 * These tests verify equipment functionality and will fail until implementation is complete.
 */

import { test, expect } from '@playwright/test';

test.describe('Equipment Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Navigate to equipment page
    await page.click('[data-testid="equipment-nav-link"]');
    await expect(page.locator('[data-testid="equipment-page"]')).toBeVisible();
  });

  test('should display equipment list', async ({ page }) => {
    // Should show equipment list container
    const equipmentList = page.locator('[data-testid="equipment-list"]');
    await expect(equipmentList).toBeVisible();
    
    // Should show add equipment button
    const addButton = page.locator('[data-testid="add-equipment-button"]');
    await expect(addButton).toBeVisible();
    
    // Should show equipment categories filter
    const categoryFilter = page.locator('[data-testid="equipment-category-filter"]');
    await expect(categoryFilter).toBeVisible();
  });

  test('should add new equipment', async ({ page }) => {
    // Click add equipment button
    await page.click('[data-testid="add-equipment-button"]');
    
    // Should show add equipment modal/form
    const addForm = page.locator('[data-testid="add-equipment-form"]');
    await expect(addForm).toBeVisible();
    
    // Fill out equipment details
    await page.fill('[data-testid="equipment-name-input"]', 'Adjustable Dumbbells');
    await page.selectOption('[data-testid="equipment-category-select"]', 'weights');
    await page.selectOption('[data-testid="equipment-condition-select"]', 'excellent');
    
    // Add specifications
    await page.fill('[data-testid="weight-range-input"]', '5-50 lbs');
    await page.fill('[data-testid="adjustment-type-input"]', 'dial');
    
    // Save equipment
    await page.click('[data-testid="save-equipment-button"]');
    
    // Should show success message
    const successMessage = page.locator('[data-testid="equipment-added-success"]');
    await expect(successMessage).toBeVisible();
    
    // Should appear in equipment list
    const newEquipment = page.locator('[data-testid="equipment-item"]').filter({ hasText: 'Adjustable Dumbbells' });
    await expect(newEquipment).toBeVisible();
  });

  test('should validate equipment form', async ({ page }) => {
    await page.click('[data-testid="add-equipment-button"]');
    
    // Try to save without required fields
    await page.click('[data-testid="save-equipment-button"]');
    
    // Should show validation errors
    const nameError = page.locator('[data-testid="equipment-name-error"]');
    await expect(nameError).toBeVisible();
    await expect(nameError).toContainText('required');
    
    const categoryError = page.locator('[data-testid="equipment-category-error"]');
    await expect(categoryError).toBeVisible();
    
    // Should highlight required fields
    const nameInput = page.locator('[data-testid="equipment-name-input"]');
    await expect(nameInput).toHaveClass(/error/);
  });

  test('should edit existing equipment', async ({ page }) => {
    // Assume there's existing equipment
    const firstEquipment = page.locator('[data-testid="equipment-item"]').first();
    await expect(firstEquipment).toBeVisible();
    
    // Click edit button
    await firstEquipment.locator('[data-testid="edit-equipment-button"]').click();
    
    // Should show edit form
    const editForm = page.locator('[data-testid="edit-equipment-form"]');
    await expect(editForm).toBeVisible();
    
    // Should pre-populate form with existing data
    const nameInput = page.locator('[data-testid="equipment-name-input"]');
    await expect(nameInput).not.toHaveValue('');
    
    // Modify equipment
    await nameInput.fill('Updated Equipment Name');
    await page.selectOption('[data-testid="equipment-condition-select"]', 'good');
    
    // Save changes
    await page.click('[data-testid="save-equipment-button"]');
    
    // Should show update success
    const updateMessage = page.locator('[data-testid="equipment-updated-success"]');
    await expect(updateMessage).toBeVisible();
    
    // Should reflect changes in list
    const updatedEquipment = page.locator('[data-testid="equipment-item"]').filter({ hasText: 'Updated Equipment Name' });
    await expect(updatedEquipment).toBeVisible();
  });

  test('should delete equipment', async ({ page }) => {
    const firstEquipment = page.locator('[data-testid="equipment-item"]').first();
    await expect(firstEquipment).toBeVisible();
    
    // Get equipment name for verification
    const equipmentName = await firstEquipment.locator('[data-testid="equipment-name"]').textContent();
    
    // Click delete button
    await firstEquipment.locator('[data-testid="delete-equipment-button"]').click();
    
    // Should show confirmation dialog
    const confirmDialog = page.locator('[data-testid="delete-confirmation-dialog"]');
    await expect(confirmDialog).toBeVisible();
    await expect(confirmDialog).toContainText(equipmentName || '');
    
    // Confirm deletion
    await page.click('[data-testid="confirm-delete-button"]');
    
    // Should show deletion success
    const deleteMessage = page.locator('[data-testid="equipment-deleted-success"]');
    await expect(deleteMessage).toBeVisible();
    
    // Should be removed from list
    const deletedEquipment = page.locator('[data-testid="equipment-item"]').filter({ hasText: equipmentName || '' });
    await expect(deletedEquipment).toBeHidden();
  });

  test('should filter equipment by category', async ({ page }) => {
    // Select weights category
    await page.selectOption('[data-testid="equipment-category-filter"]', 'weights');
    
    // Should only show weights equipment
    const equipmentItems = page.locator('[data-testid="equipment-item"]');
    const count = await equipmentItems.count();
    
    if (count > 0) {
      // All visible items should be weights category
      for (let i = 0; i < count; i++) {
        const item = equipmentItems.nth(i);
        const category = item.locator('[data-testid="equipment-category"]');
        await expect(category).toContainText('weights');
      }
    }
    
    // Clear filter
    await page.selectOption('[data-testid="equipment-category-filter"]', 'all');
    
    // Should show all equipment again
    const allItems = page.locator('[data-testid="equipment-item"]');
    const allCount = await allItems.count();
    expect(allCount).toBeGreaterThanOrEqual(count);
  });

  test('should search equipment', async ({ page }) => {
    // Type in search box
    await page.fill('[data-testid="equipment-search-input"]', 'dumbbell');
    
    // Should filter results
    const searchResults = page.locator('[data-testid="equipment-item"]');
    const resultCount = await searchResults.count();
    
    if (resultCount > 0) {
      // All results should contain search term
      for (let i = 0; i < resultCount; i++) {
        const item = searchResults.nth(i);
        const name = item.locator('[data-testid="equipment-name"]');
        await expect(name).toContainText(/dumbbell/i);
      }
    }
    
    // Clear search
    await page.fill('[data-testid="equipment-search-input"]', '');
    
    // Should show all equipment
    const allResults = page.locator('[data-testid="equipment-item"]');
    const allCount = await allResults.count();
    expect(allCount).toBeGreaterThanOrEqual(resultCount);
  });

  test('should toggle equipment availability', async ({ page }) => {
    const firstEquipment = page.locator('[data-testid="equipment-item"]').first();
    await expect(firstEquipment).toBeVisible();
    
    // Check current availability status
    const availabilityToggle = firstEquipment.locator('[data-testid="equipment-availability-toggle"]');
    const initialState = await availabilityToggle.isChecked();
    
    // Toggle availability
    await availabilityToggle.click();
    
    // Should show status change
    const statusMessage = page.locator('[data-testid="availability-updated"]');
    await expect(statusMessage).toBeVisible();
    
    // Should reflect new state
    await expect(availabilityToggle).toBeChecked({ checked: !initialState });
    
    // Should update visual indicator
    const statusIndicator = firstEquipment.locator('[data-testid="equipment-status-indicator"]');
    if (initialState) {
      await expect(statusIndicator).toHaveClass(/unavailable/);
    } else {
      await expect(statusIndicator).toHaveClass(/available/);
    }
  });

  test('should show equipment details', async ({ page }) => {
    const firstEquipment = page.locator('[data-testid="equipment-item"]').first();
    await expect(firstEquipment).toBeVisible();
    
    // Click to view details
    await firstEquipment.click();
    
    // Should show equipment details modal/page
    const detailsModal = page.locator('[data-testid="equipment-details-modal"]');
    await expect(detailsModal).toBeVisible();
    
    // Should show all equipment information
    await expect(detailsModal.locator('[data-testid="equipment-name"]')).toBeVisible();
    await expect(detailsModal.locator('[data-testid="equipment-category"]')).toBeVisible();
    await expect(detailsModal.locator('[data-testid="equipment-condition"]')).toBeVisible();
    await expect(detailsModal.locator('[data-testid="equipment-specifications"]')).toBeVisible();
    
    // Should have action buttons
    await expect(detailsModal.locator('[data-testid="edit-equipment-button"]')).toBeVisible();
    await expect(detailsModal.locator('[data-testid="delete-equipment-button"]')).toBeVisible();
    
    // Close details
    await page.click('[data-testid="close-details-button"]');
    await expect(detailsModal).toBeHidden();
  });

  test('should import equipment from template', async ({ page }) => {
    // Click import button
    await page.click('[data-testid="import-equipment-button"]');
    
    // Should show import options
    const importModal = page.locator('[data-testid="import-equipment-modal"]');
    await expect(importModal).toBeVisible();
    
    // Should show equipment templates
    const templates = page.locator('[data-testid="equipment-template"]');
    await expect(templates.first()).toBeVisible();
    
    // Select a template (e.g., "Home Gym Starter")
    const homeGymTemplate = templates.filter({ hasText: 'Home Gym Starter' });
    await homeGymTemplate.click();
    
    // Should show template contents
    const templateItems = page.locator('[data-testid="template-equipment-item"]');
    await expect(templateItems.first()).toBeVisible();
    
    // Import selected items
    await page.click('[data-testid="import-selected-button"]');
    
    // Should show import success
    const importSuccess = page.locator('[data-testid="equipment-imported-success"]');
    await expect(importSuccess).toBeVisible();
    
    // Should add items to equipment list
    const equipmentList = page.locator('[data-testid="equipment-item"]');
    const finalCount = await equipmentList.count();
    expect(finalCount).toBeGreaterThan(0);
  });

  test('should export equipment list', async ({ page }) => {
    // Click export button
    await page.click('[data-testid="export-equipment-button"]');
    
    // Should show export options
    const exportModal = page.locator('[data-testid="export-equipment-modal"]');
    await expect(exportModal).toBeVisible();
    
    // Select export format
    await page.selectOption('[data-testid="export-format-select"]', 'json');
    
    // Start export
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="start-export-button"]');
    
    // Should trigger download
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('equipment');
    expect(download.suggestedFilename()).toContain('.json');
  });

  test('should sync equipment data', async ({ page }) => {
    // Should show sync status
    const syncStatus = page.locator('[data-testid="equipment-sync-status"]');
    await expect(syncStatus).toBeVisible();
    
    // Trigger manual sync
    await page.click('[data-testid="sync-equipment-button"]');
    
    // Should show sync in progress
    const syncProgress = page.locator('[data-testid="sync-in-progress"]');
    await expect(syncProgress).toBeVisible();
    
    // Should complete sync
    const syncComplete = page.locator('[data-testid="sync-completed"]');
    await expect(syncComplete).toBeVisible({ timeout: 10000 });
    
    // Should update sync timestamp
    const lastSync = page.locator('[data-testid="last-sync-time"]');
    await expect(lastSync).toContainText(/just now|seconds ago/);
  });

  test('should handle equipment recommendations', async ({ page }) => {
    // Click recommendations button
    await page.click('[data-testid="equipment-recommendations-button"]');
    
    // Should show recommendations based on goals
    const recommendations = page.locator('[data-testid="equipment-recommendations"]');
    await expect(recommendations).toBeVisible();
    
    // Should show recommended items
    const recommendedItems = page.locator('[data-testid="recommended-equipment-item"]');
    await expect(recommendedItems.first()).toBeVisible();
    
    // Should show reason for recommendation
    const recommendationReason = recommendedItems.first().locator('[data-testid="recommendation-reason"]');
    await expect(recommendationReason).toBeVisible();
    
    // Should allow adding recommended equipment
    await recommendedItems.first().locator('[data-testid="add-recommended-equipment"]').click();
    
    // Should add to equipment list
    const addedEquipment = page.locator('[data-testid="equipment-added-from-recommendation"]');
    await expect(addedEquipment).toBeVisible();
  });

  test('should work offline', async ({ page }) => {
    // Load equipment data while online
    await expect(page.locator('[data-testid="equipment-list"]')).toBeVisible();
    
    // Go offline
    await page.context().setOffline(true);
    
    // Reload page
    await page.reload();
    
    // Should still show cached equipment
    await expect(page.locator('[data-testid="equipment-list"]')).toBeVisible();
    
    // Should show offline indicator
    const offlineIndicator = page.locator('[data-testid="offline-indicator"]');
    await expect(offlineIndicator).toBeVisible();
    
    // Should allow adding equipment offline
    await page.click('[data-testid="add-equipment-button"]');
    await page.fill('[data-testid="equipment-name-input"]', 'Offline Equipment');
    await page.selectOption('[data-testid="equipment-category-select"]', 'cardio');
    await page.click('[data-testid="save-equipment-button"]');
    
    // Should save locally with sync pending
    const pendingSync = page.locator('[data-testid="pending-sync-indicator"]');
    await expect(pendingSync).toBeVisible();
  });
});
