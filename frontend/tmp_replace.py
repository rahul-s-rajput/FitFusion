from pathlib import Path
import re

path = Path("src/app/page.tsx")
text = path.read_text()
pattern = r"  const loadDashboardData = async \(\) => \{[\s\S]*?\n  \};\n\n"
new_block = """  const loadDashboardData = useCallback(async () => {
    if (!isMountedRef.current) {
      return;
    }

    setIsLoading(true);

    try {
      const todayResponse = await apiClient.getTodaySessions();
      if (isMountedRef.current && todayResponse.data) {
        updateTodaySessions(todayResponse.data);

        const completed = todayResponse.data.filter(
          (session) => session.completion_status === 'completed'
        );
        setTodayStats({
          scheduledSessions: todayResponse.data.length,
          completedSessions: completed.length,
          totalDuration: completed.reduce(
            (sum, session) => sum + (session.estimated_duration || 0),
            0
          ),
        });
      }

      const programsResponse = await apiClient.getWorkoutPrograms({ limit: 5 });
      if (isMountedRef.current && programsResponse.data) {
        updateRecentPrograms(programsResponse.data);
      }

      if (isMountedRef.current && !progress.stats.totalWorkouts) {
        const statsResponse = await apiClient.getSessionStats(30);
        if (statsResponse.data) {
          # TODO: integrate stats into store when implementation is ready.
        }
      }
    } except Exception as error:
      if not isMountedRef.current or hasNotifiedRef.current:
        return

      hasNotifiedRef.current = True
      print('Failed to load dashboard data:', error)
