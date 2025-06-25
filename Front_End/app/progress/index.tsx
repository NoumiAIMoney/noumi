import React, { JSX, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { MaterialIcons } from '@expo/vector-icons';
import HomeIcon from '@/assets/icons/home.svg'; 
import GoalsIcon from '@/assets/icons//goals.svg'; 
import ProgressIcon from '@/assets/icons//progress.svg';
import { colors, typography, shadows } from '@/src/theme';
import { router } from 'expo-router';

// Type definitions
interface Habit {
  completed: number;
  total: number;
  isCompleted: boolean;
}

interface HabitsState {
  [key: string]: Habit;
}

interface ProgressScreenProps {
  navigation: {
    goBack: () => void;
    navigate: (screen: string) => void;
  };
}

type TabType = 'Active Habits' | 'Weekly Recaps';

const ProgressScreen: React.FC<ProgressScreenProps> = ({ navigation }) => {
  const [activeTab, setActiveTab] = useState<TabType>('Active Habits');
  const [habits, setHabits] = useState<HabitsState>({
    'Eat at home twice': { completed: 1, total: 4, isCompleted: false },
    'Try a No-Spend-Day': { completed: 0, total: 1, isCompleted: false },
    'Log in to Noumi daily': { completed: 7, total: 7, isCompleted: true }
  });

  const toggleHabit = (habitName: string): void => {
    setHabits(prev => {
      const newHabits = { ...prev };
      const habit = newHabits[habitName];

      if (!habit.isCompleted && habit.completed < habit.total) {
        habit.completed += 1;
        if (habit.completed === habit.total) {
          habit.isCompleted = true;
        }
      }

      return newHabits;
    });
  };

  // Calculate overall progress percentage for current month
  const calculateCurrentMonthProgress = (): number => {
    const habitEntries = Object.entries(habits);
    const totalTasks = habitEntries.reduce((sum, [_, habit]) => sum + habit.total, 0);
    const completedTasks = habitEntries.reduce((sum, [_, habit]) => sum + habit.completed, 0);
    return totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
  };

  const getHabitsList = (): [string, Habit][] => {
    const habitEntries = Object.entries(habits);

    // Separate incomplete and complete habits
    const incomplete = habitEntries.filter(([_, habit]) => !habit.isCompleted);
    const complete = habitEntries.filter(([_, habit]) => habit.isCompleted);

    // Sort incomplete habits by completion percentage (ascending - least completed first)
    incomplete.sort(([, a], [, b]) => {
      const aPercentage = (a.completed / a.total) * 100;
      const bPercentage = (b.completed / b.total) * 100;
      return aPercentage - bPercentage;
    });

    // Sort completed habits by completion order (could be by name or keep original order)
    complete.sort(([nameA], [nameB]) => nameA.localeCompare(nameB));

    // Return incomplete habits first (least completed at top), then completed habits
    return [...incomplete, ...complete];
  };

  const renderActiveHabits = (): JSX.Element => {
    const currentMonthProgress = calculateCurrentMonthProgress();

    return (
      <View style={styles.content}>
        <Text style={styles.statsTitle}>Habit Stats</Text>
        {/* Habit Stats */}
        <View style={styles.statsCard}>
          <View style={styles.statsRow}>
            <View style={styles.statsNumber}>
              <Text style={styles.statsCount}>3</Text>
              <Text style={styles.statsLabel}>Habits</Text>
              <Text style={styles.statsSubLabel}>This Year</Text>
            </View>
            <View style={styles.calendarGrid}>
              {Array.from({ length: 12 }, (_, i) => {
                const currentMonth = new Date().getMonth(); // 0-11
                const isCurrentMonth = i === currentMonth;
                const progressHeight = isCurrentMonth ? (currentMonthProgress / 100) * 35 : 0;

                return (
                  <View key={`dot-container-${i}`} style={[styles.calendarDotContainer, { left: `${4 + i * 8}%` }]}>
                    {/* Background dot */}
                    <View style={[styles.calendarDot]} />
                    {/* Progress fill */}
                    {isCurrentMonth && (
                      <View 
                        style={[
                          styles.calendarDotProgress, 
                          { 
                            height: progressHeight,
                            bottom: 0,
                          }
                        ]} 
                      />
                    )}
                    {/* Completed months (example: previous months could be fully filled) */}
                    {i < currentMonth && (
                      <View style={[styles.calendarDotCompleted]} />
                    )}
                  </View>
                );
              })}
              <View style={styles.monthLabels}>
                {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((month, i) => (
                  <Text key={`month-${i}`} style={styles.monthLabel}>{month.charAt(0)}</Text>
                ))}
              </View>
            </View>
          </View>
        </View>

        {/* Habits for the week */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Habits for the week</Text>
          <Text style={styles.sectionSubtitle}>When you complete a habit, mark it as done!</Text>

          <View style={styles.habitsList}>
            {getHabitsList().map(([habitName, habit]) => (
              <View key={habitName} style={styles.habitCard}>
                <View style={styles.habitContent}>
                  <Text style={styles.habitText}>{habitName}</Text>
                  <View style={styles.habitProgress}>
                    <View style={styles.progressBar}>
                      <View 
                        style={[
                          styles.progressFill, 
                          { 
                            width: `${(habit.completed / habit.total) * 100}%`,
                            backgroundColor: habit.isCompleted ? colors.primaryGreen : colors.progressBarOrange
                          }
                        ]} 
                      />
                    </View>
                    <Text style={styles.progressText}>
                      {habit.completed} out of {habit.total} complete
                    </Text>
                  </View>
                </View>
                <TouchableOpacity 
                  style={styles.checkButton}
                  onPress={() => toggleHabit(habitName)}
                  disabled={habit.isCompleted}
                >
                  {habit.isCompleted ? (
                    <View style={styles.checkedButton}>
                      <Ionicons name="checkmark" size={16} color={colors.white} />
                    </View>
                  ) : (
                    <View style={styles.uncheckedButton} />
                  )}
                </TouchableOpacity>
              </View>
            ))}
          </View>
        </View>
      </View>
    );
  };

  const renderWeeklyRecaps = (): JSX.Element => (
    <View style={styles.content}>
      <Text style={styles.recapTitle}>Check your weekly progress</Text>
      <Text style={styles.recapSubtitle}>You can find all your weekly recaps here</Text>

      <View style={styles.recapsList}>
        {[
          '05/26 - 05/31',
          '05/19 - 05/26', 
          '05/12 - 05/19',
          '05/05 - 05/12',
          '04/29 - 05/05'
        ].map((dateRange: string, index: number) => (
          <TouchableOpacity key={index} style={styles.recapCard} onPress={()=>router.replace('/weekly-recap')}>
            <View style={styles.recapContent}>
              <View style={styles.recapIcon}>
                <MaterialIcons name="emoji-events" size={24} color={colors.white} />
              </View>
              <View style={styles.recapText}>
                <Text style={styles.recapDate}>{dateRange}</Text>
                <Text style={styles.recapCardTitle}>Your Weekly Recap</Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.lightGrayFont} />
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => router.replace('/home-screen')}
        >
          <Ionicons name="chevron-back" size={24} color={colors.gray} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Progress</Text>
        <View style={styles.headerRight} />
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'Active Habits' && styles.activeTab]}
          onPress={() => setActiveTab('Active Habits')}
        >
          <Text style={[styles.tabText, activeTab === 'Active Habits' && styles.activeTabText]}>
            Active Habits
          </Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'Weekly Recaps' && styles.activeTab]}
          onPress={() => setActiveTab('Weekly Recaps')}
        >
          <Text style={[styles.tabText, activeTab === 'Weekly Recaps' && styles.activeTabText]}>
            Weekly Recaps
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {activeTab === 'Active Habits' ? renderActiveHabits() : renderWeeklyRecaps()}
      </ScrollView>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <TouchableOpacity 
          style={styles.navItem}
          onPress={() => navigation.navigate('Home')}
        >
          <HomeIcon />
          <Text style={styles.navText}>Home</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.navItem}>
          <GoalsIcon />
          <Text style={styles.navText}>Goals</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.navItem}>
          <ProgressIcon/>
          <Text style={styles.navTextActive}>Progress</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.lightBackground,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 20,
    backgroundColor: colors.lightBackground,
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontSize: typography.fontSize.large,
    fontWeight: '600',
    color: colors.darkFont,
  },
  headerRight: {
    width: 32,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: colors.lightBackground,
    paddingHorizontal: 20,
    marginBottom: 40,
    alignContent: 'center',
    justifyContent: 'center',
  },
  tab: {
    paddingVertical: 12,
    paddingHorizontal: 0,
    marginRight: 30,
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primaryGreen,
  },
  tabText: {
    fontSize: typography.fontSize.body,
    color: colors.darkFont,
    fontWeight: '500',
  },
  activeTabText: {
    color: colors.primaryGreen,
    fontWeight: '500',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 20,
  },
  statsCard: {
    backgroundColor: colors.white,
    borderRadius: 16,
    padding: 20,
    marginBottom: 30,
    ...shadows.input,
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  statsTitle: {
    fontSize: typography.fontSize.large,
    fontWeight: '600',
    color: colors.darkFont,
    marginBottom: 20,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statsNumber: {
    marginRight: 30,
  },
  statsCount: {
    fontSize: 48,
    fontWeight: 'bold',
    color: colors.primaryGreen,
    lineHeight: 50,
  },
  statsLabel: {
    fontSize: typography.fontSize.small,
    color: colors.primaryGreen,
    fontWeight: '600',
  },
  statsSubLabel: {
    fontSize: typography.fontSize.mini,
    color: colors.muted,
    fontWeight: '600',
  },
  calendarGrid: {
    flex: 1,
    position: 'relative',
  },
  calendarDotContainer: {
    position: 'absolute',
    width: 6,
    height: 35,
    top: -20,
  },
  calendarDot: {
    position: 'absolute',
    width: 6,
    height: 35,
    backgroundColor: colors.progressBarOrangeLight,
    borderRadius: 25,
    top: 0,
  },
  calendarDotProgress: {
    position: 'absolute',
    width: 6,
    backgroundColor: colors.progressBarOrange,
    borderRadius: 25,
  },
  calendarDotCompleted: {
    position: 'absolute',
    width: 6,
    height: 35,
    borderRadius: 25,
    top: 0,
  },
  monthLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
    gap: 8,
  },
  monthLabel: {
    fontSize: typography.fontSize.mini,
    color: colors.muted,
    textAlign: 'center',
    fontWeight: '700',
    flex: 1,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: typography.fontSize.large,
    fontWeight: '600',
    color: colors.darkFont,
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: typography.fontSize.small,
    color: colors.darkFont,
    marginBottom: 20,
    fontWeight: '400',
  },
  habitsList: {
    gap: 12,
  },
  habitCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    ...shadows.input,
    width: 370,
    height: 89,
  },
  habitContent: {
    flex: 1,
  },
  habitText: {
    fontSize: typography.fontSize.body,
    color: colors.darkFont,
    marginBottom: 8,
    fontWeight: '500',
  },
  habitProgress: {
    gap: 4,
  },
  progressBar: {
    height: 11,
    backgroundColor: colors.progressBarOrangeLight,
    borderRadius: 8,
    width: 170,
  },
  progressFill: {
    height: '100%',
    borderRadius: 8,
  },
  progressText: {
    fontSize: typography.fontSize.mini,
    color: colors.darkFont,
  },
  checkButton: {
    marginLeft: 16,
  },
  uncheckedButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: colors.lightGrayFont,
  },
  checkedButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.primaryGreen,
    justifyContent: 'center',
    alignItems: 'center',
  },
  recapTitle: {
    fontSize: typography.fontSize.large,
    fontWeight: '600',
    color: colors.darkFont,
    marginBottom: 8,
  },
  recapSubtitle: {
    fontSize: typography.fontSize.body,
    color: colors.darkFont,
    marginBottom: 20,
  },
  recapsList: {
    gap: 16,
  },
  recapCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.07,
    shadowRadius: 2,
    elevation: 1,
    width: 353,
    height: 57,
  },
  recapContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recapIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primaryGreen,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  recapText: {
    flex: 1,
    color: colors.darkFont,
  },
  recapDate: {
    fontSize: typography.fontSize.mini,
    color: colors.lightGrayFont,
    marginBottom: 2,
  },
  recapCardTitle: {
    fontSize: typography.fontSize.body,
    fontWeight: '500',
    color: colors.gray,
  },
  bottomNav: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    backgroundColor: colors.white,
    paddingTop: 15,
    paddingBottom: 15,
    paddingHorizontal: 20,
    bottom: -30,
  },
  navItem: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  navText: {
    fontSize: typography.fontSize.mini,
    color: colors.disabled,
    marginTop: 4,
  },
  navTextActive: {
    fontSize: typography.fontSize.mini,
    color: colors.primaryGreen,
    marginTop: 4,
    fontWeight: '600',
  },
});

export default ProgressScreen;