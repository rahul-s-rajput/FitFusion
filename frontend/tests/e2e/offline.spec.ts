/**
 * Offline Workout Execution Integration Tests
 * These tests verify offline functionality and will fail until implementation is complete.
 */

import { test, expect } from '@playwright/test';

test.describe('Offline Workout Execution', () => {
  test.beforeEach(async ({ page }) => {
    // Start online to load initial data
    await page.context().setOffline(false);
    await page.goto('/');
    
    // Wait for initial data to load and cache
    await expect(page.locator('[data-testid="app-loaded"]')).toBeVisible({ timeout: 10000 });
  });

  test('should load workout data from local storage when offline', async ({ page }) => {
    // Navigate to workouts page while online
    await page.click('[data-testid="workouts-nav-link"]');
    await expect(page.locator('[data-testid="workout-list"]')).toBeVisible();
    
    // Go offline
    await page.context().setOffline(true);
    
    // Reload the page
    await page.reload();
    
    // Should still show cached workout data
    await expect(page.locator('[data-testid="workout-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="offline-indicator"]')).toBeVisible();
    
    // Should show offline message
    const offlineMessage = page.locator('[data-testid="offline-mode-message"]');
    await expect(offlineMessage).toContainText('offline');
  });

  test('should execute workout completely offline', async ({ page }) => {
    // Load a workout while online
    await page.click('[data-testid="workouts-nav-link"]');
    await page.click('[data-testid="workout-item"]:first-child');
    await expect(page.locator('[data-testid="workout-details"]')).toBeVisible();
    
    // Go offline
    await page.context().setOffline(true);
    
    // Start the workout
    await page.click('[data-testid="start-workout-button"]');
    await expect(page.locator('[data-testid="workout-execution-screen"]')).toBeVisible();
    
    // Should show current exercise
    await expect(page.locator('[data-testid="current-exercise"]')).toBeVisible();
    
    // Should have working timer
    const timer = page.locator('[data-testid="exercise-timer"]');
    await expect(timer).toBeVisible();
    
    // Complete first exercise
    await page.click('[data-testid="complete-exercise-button"]');
    
    // Should move to next exercise or rest period
    const nextStep = page.locator('[data-testid="next-exercise"], [data-testid="rest-period"]');
    await expect(nextStep).toBeVisible();
    
    // Should save progress locally
    const progressSaved = page.locator('[data-testid="progress-saved-locally"]');
    await expect(progressSaved).toBeVisible({ timeout: 5000 });
  });

  test('should handle exercise modifications offline', async ({ page }) => {
    // Start a workout offline
    await page.context().setOffline(true);
    await page.goto('/workout/today');
    
    await page.click('[data-testid="start-workout-button"]');
    await expect(page.locator('[data-testid="workout-execution-screen"]')).toBeVisible();
    
    // Modify exercise (e.g., reduce reps due to fatigue)
    await page.click('[data-testid="modify-exercise-button"]');
    await page.fill('[data-testid="reps-input"]', '8'); // Reduce from default
    await page.click('[data-testid="save-modification-button"]');
    
    // Should save modification locally
    const modificationSaved = page.locator('[data-testid="modification-saved"]');
    await expect(modificationSaved).toBeVisible();
    
    // Should show modified values
    const repsDisplay = page.locator('[data-testid="current-reps"]');
    await expect(repsDisplay).toContainText('8');
  });

  test('should track workout progress offline', async ({ page }) => {
    // Go offline and start workout
    await page.context().setOffline(true);
    await page.goto('/workout/today');
    
    await page.click('[data-testid="start-workout-button"]');
    
    // Complete several exercises
    for (let i = 0; i < 3; i++) {
      await page.click('[data-testid="complete-exercise-button"]');
      await page.waitForTimeout(1000); // Wait for UI updates
    }
    
    // Check progress indicator
    const progressBar = page.locator('[data-testid="workout-progress-bar"]');
    await expect(progressBar).toBeVisible();
    
    const progressText = page.locator('[data-testid="workout-progress-text"]');
    await expect(progressText).toContainText('3'); // Should show 3 exercises completed
    
    // Should save progress to local storage
    const localProgress = await page.evaluate(() => {
      return localStorage.getItem('workout-progress');
    });
    expect(localProgress).toBeTruthy();
  });

  test('should complete workout and save results offline', async ({ page }) => {
    // Start and complete entire workout offline
    await page.context().setOffline(true);
    await page.goto('/workout/today');
    
    await page.click('[data-testid="start-workout-button"]');
    
    // Fast-forward through workout (simulate completion)
    await page.evaluate(() => {
      // Mock workout completion
      window.dispatchEvent(new CustomEvent('workout-completed', {
        detail: {
          duration: 1800, // 30 minutes
          exercisesCompleted: 8,
          caloriesBurned: 250
        }
      }));
    });
    
    // Should show completion screen
    await expect(page.locator('[data-testid="workout-completion-screen"]')).toBeVisible();
    
    // Should display workout summary
    const summary = page.locator('[data-testid="workout-summary"]');
    await expect(summary).toBeVisible();
    await expect(summary).toContainText('30'); // Duration in minutes
    await expect(summary).toContainText('8'); // Exercises completed
    
    // Should save results locally with sync pending flag
    const pendingSync = page.locator('[data-testid="pending-sync-badge"]');
    await expect(pendingSync).toBeVisible();
  });

  test('should handle offline equipment substitutions', async ({ page }) => {
    // Go offline and start workout
    await page.context().setOffline(true);
    await page.goto('/workout/today');
    
    await page.click('[data-testid="start-workout-button"]');
    
    // Encounter exercise requiring unavailable equipment
    await page.click('[data-testid="equipment-unavailable-button"]');
    
    // Should show offline substitution options
    const substitutions = page.locator('[data-testid="offline-substitutions"]');
    await expect(substitutions).toBeVisible();
    
    // Should have pre-cached alternatives
    const alternatives = page.locator('[data-testid="exercise-alternative"]');
    await expect(alternatives.first()).toBeVisible();
    
    // Select alternative
    await alternatives.first().click();
    
    // Should update workout with substitution
    const substitutionConfirm = page.locator('[data-testid="substitution-applied"]');
    await expect(substitutionConfirm).toBeVisible();
  });

  test('should sync workout data when connection restored', async ({ page }) => {
    // Complete workout offline
    await page.context().setOffline(true);
    await page.goto('/workout/today');
    
    // Simulate completed workout
    await page.evaluate(() => {
      localStorage.setItem('pending-workout-sync', JSON.stringify({
        workoutId: 'workout-123',
        completedAt: new Date().toISOString(),
        duration: 1800,
        exercisesCompleted: 8,
        syncStatus: 'pending'
      }));
    });
    
    // Go back online
    await page.context().setOffline(false);
    await page.reload();
    
    // Should automatically sync
    const syncInProgress = page.locator('[data-testid="sync-in-progress"]');
    await expect(syncInProgress).toBeVisible({ timeout: 5000 });
    
    // Should show sync completion
    const syncComplete = page.locator('[data-testid="sync-completed"]');
    await expect(syncComplete).toBeVisible({ timeout: 10000 });
    
    // Pending sync badge should disappear
    const pendingSync = page.locator('[data-testid="pending-sync-badge"]');
    await expect(pendingSync).toBeHidden();
  });

  test('should handle workout timer offline', async ({ page }) => {
    // Start workout offline
    await page.context().setOffline(true);
    await page.goto('/workout/today');
    
    await page.click('[data-testid="start-workout-button"]');
    
    // Should have working exercise timer
    const exerciseTimer = page.locator('[data-testid="exercise-timer"]');
    await expect(exerciseTimer).toBeVisible();
    
    // Timer should count down
    const initialTime = await exerciseTimer.textContent();
    await page.waitForTimeout(2000);
    const updatedTime = await exerciseTimer.textContent();
    
    expect(initialTime).not.toBe(updatedTime);
    
    // Should have rest timer
    await page.click('[data-testid="complete-exercise-button"]');
    const restTimer = page.locator('[data-testid="rest-timer"]');
    await expect(restTimer).toBeVisible();
    
    // Should auto-advance after rest period
    await page.evaluate(() => {
      // Fast-forward rest timer
      window.dispatchEvent(new CustomEvent('rest-period-complete'));
    });
    
    const nextExercise = page.locator('[data-testid="next-exercise"]');
    await expect(nextExercise).toBeVisible();
  });

  test('should maintain workout state during offline session', async ({ page }) => {
    // Start workout offline
    await page.context().setOffline(true);
    await page.goto('/workout/today');
    
    await page.click('[data-testid="start-workout-button"]');
    
    // Complete some exercises
    await page.click('[data-testid="complete-exercise-button"]');
    await page.click('[data-testid="complete-exercise-button"]');
    
    // Simulate app refresh/reload
    await page.reload();
    
    // Should restore workout state
    await expect(page.locator('[data-testid="workout-in-progress"]')).toBeVisible();
    
    // Should show correct progress
    const progressText = page.locator('[data-testid="workout-progress-text"]');
    await expect(progressText).toContainText('2'); // 2 exercises completed
    
    // Should have resume button
    const resumeButton = page.locator('[data-testid="resume-workout-button"]');
    await expect(resumeButton).toBeVisible();
    
    await resumeButton.click();
    await expect(page.locator('[data-testid="workout-execution-screen"]')).toBeVisible();
  });

  test('should show offline capabilities in workout list', async ({ page }) => {
    // Go offline
    await page.context().setOffline(true);
    await page.goto('/workouts');
    
    // Should show which workouts are available offline
    const offlineWorkouts = page.locator('[data-testid="offline-available-badge"]');
    await expect(offlineWorkouts.first()).toBeVisible();
    
    // Should disable workouts not cached offline
    const onlineOnlyWorkouts = page.locator('[data-testid="online-only-workout"]');
    if (await onlineOnlyWorkouts.count() > 0) {
      await expect(onlineOnlyWorkouts.first()).toHaveClass(/disabled/);
    }
    
    // Should show offline storage usage
    const storageInfo = page.locator('[data-testid="offline-storage-info"]');
    await expect(storageInfo).toBeVisible();
  });
});
