import GoalsIcon from '@/assets/icons/goals.svg';
import HomeIcon from '@/assets/icons/home.svg';
import ProgressIcon from '@/assets/icons/progress.svg';
import HabitCard, { HydratedHabit, hydrateHabits } from '@/components/HabitCard';
import RecapCard from '@/components/RecapCard';
import { getYearlyAnomalies } from '@/src/api/anomalies';
import { getHabits } from '@/src/api/habits';
import { colors, typography } from '@/src/theme';
import { getPastFiveWeekRanges } from '@/src/utils/formatters';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import React, { JSX, useEffect, useState } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';

type TabType = 'Active Habits' | 'Weekly Recaps';

const ProgressScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('Active Habits');
  const [habits, setHabits] = useState<HydratedHabit[]>([]);
  const [anomalies, setAnomalies] = useState<number[]>([]);

  useEffect(() => {
    async function fetchAndHydrateHabits() {
      try {
        const [rawHabits, anomalyData] = await Promise.all([
          getHabits(),
          getYearlyAnomalies()
        ]);
        const hydrated = hydrateHabits(rawHabits);
        setHabits(hydrated);
        setAnomalies(anomalyData.anomalies);
      } catch (err) {
        console.error('Failed to fetch habits:', err);
      }
    }

    fetchAndHydrateHabits();
  }, []);

  const toggleHabit = (habitName: string) => {
    const updatedHabits = habits.map(habit => {
      if (habit.name === habitName && habit.completed < habit.total) {
        const newCompleted = habit.completed + 1;
        return {
          ...habit,
          completed: newCompleted,
          isCompleted: newCompleted === habit.total,
        };
      }
      return habit;
    });

    const sorted = sortHabits(updatedHabits);
    setHabits(sorted);
  };

  const sortHabits = (list: HydratedHabit[]): HydratedHabit[] => {
    const incomplete = list.filter(h => h.completed < h.total);
    const complete = list.filter(h => h.completed >= h.total);
    return [...incomplete, ...complete];
  };

  const renderActiveHabits = (): JSX.Element => (
    <View style={styles.content}>
      {/* <Text style={styles.statsTitle}>Habit Stats</Text>
      <View style={styles.spikeCard}>
        <SpikeBar progress={anomalies} habitCount={3} width={373} />
      </View> */}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Habits for the week</Text>
        <Text style={styles.sectionSubtitle}>When you complete a habit, mark it as done!</Text>
        <ScrollView
          style={styles.habitsList}
          showsVerticalScrollIndicator={false}
        >
          {habits.map((habit, index) => (
            <HabitCard key={index} habit={habit} onToggle={() => toggleHabit(habit.name)} />
          ))}
        </ScrollView>
      </View>
    </View>
  );

  const renderWeeklyRecaps = (): JSX.Element => (
    <View style={styles.content}>
      <Text style={styles.recapTitle}>Check your weekly progress</Text>
      <Text style={styles.recapSubtitle}>You can find all your weekly recaps here</Text>
      <ScrollView style={[{height: 700}]}>
        {getPastFiveWeekRanges().map((dateRange, index) => (
          <RecapCard key={index} dateRange={dateRange} onPress={() => router.replace('/weekly-recap')} />
        ))}
      </ScrollView>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={{ flex: 1 }}>
        <View
          style={{ flex: 1 }}
        >
          <View style={styles.header}>
            <TouchableOpacity style={styles.backButton} onPress={() => router.replace('/home-screen')}>
              <Ionicons name="chevron-back" size={24} color={colors.gray} />
            </TouchableOpacity>
            <Text style={styles.headerTitle}>Progress</Text>
            <View style={styles.headerRight} />
          </View>

          <View style={styles.tabContainer}>
            {['Active Habits', 'Weekly Recaps'].map((tab) => {
              const isActive = activeTab === tab;
              return (
                <TouchableOpacity key={tab} style={styles.tab} onPress={() => setActiveTab(tab as TabType)}>
                  <View style={{ alignItems: 'center' }}>
                    <Text style={[styles.tabText, isActive && styles.activeTabText]}>{tab}</Text>
                    {isActive && <View style={styles.tabUnderline} />}
                  </View>
                </TouchableOpacity>
              );
            })}
          </View>

          {activeTab === 'Active Habits' ? renderActiveHabits() : renderWeeklyRecaps()}
        </View>

        {/* Fixed Bottom Navigation */}
        <View style={styles.bottomNav}>
          <TouchableOpacity style={styles.navItem} onPress={() => router.replace('/home-screen')}>
            <HomeIcon />
            <Text style={styles.navText}>Home</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.navItem}>
            <GoalsIcon />
            <Text style={styles.navText}>Goals</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.navItem} onPress={() => router.replace('/progress')}>
            <ProgressIcon />
            <Text style={styles.navTextActive}>Progress</Text>
          </TouchableOpacity>
        </View>
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
    paddingBottom: 16,
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
    paddingHorizontal: 20,
    marginBottom: 16,
    justifyContent: 'center',
  },
  tab: {
    paddingVertical: 12,
    marginRight: 30,
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
  tabUnderline: {
    marginTop: 4,
    width: 40,
    borderBottomWidth: 2,
    borderBottomColor: colors.primaryGreen,
    alignSelf: 'center',
  },
  content: {
    paddingHorizontal: 20,
  },
  statsTitle: {
    fontSize: typography.fontSize.large,
    fontWeight: '600',
    color: colors.darkFont,
    marginBottom: 8,
  },
  spikeCard: {
    marginBottom: 16,
  },
  section: {
    marginBottom: 8,
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
    marginBottom: 16,
    fontWeight: '400',
  },
  habitsList: {
    height: 432
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
  bottomNav: {
    position: 'absolute',
    bottom: -30,
    left: 0,
    right: 0,
    height: 72,
    backgroundColor: colors.white,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    zIndex: 100,
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
