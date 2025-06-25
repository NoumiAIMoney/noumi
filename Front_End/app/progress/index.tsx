import React, { JSX, useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import HomeIcon from '@/assets/icons/home.svg'; 
import GoalsIcon from '@/assets/icons//goals.svg'; 
import ProgressIcon from '@/assets/icons//progress.svg';
import { colors, typography, shadows } from '@/src/theme';
import { router } from 'expo-router';
import HabitCard, { HydratedHabit, hydrateHabits } from '@/components/HabitCard';
import { getHabits } from '@/src/api/habits';
import RecapCard from '@/components/RecapCard';
import SpikeBar from '@/components/SpikeBar';
import { getYearlyAnomalies } from '@/src/api/anomalies';

// Type definitions

interface ProgressScreenProps {
}

type TabType = 'Active Habits' | 'Weekly Recaps';

const ProgressScreen: React.FC<ProgressScreenProps> = () => {
  const [activeTab, setActiveTab] = useState<TabType>('Active Habits');
  const [habits, setHabits] = useState<HydratedHabit[]>([]);
  const [anomalies, setAnomalies] = useState<number[]>([])

  useEffect(() => {
    async function fetchAndHydrateHabits() {
      try {
        const [rawHabits, anomalyData] = await Promise.all([getHabits(), getYearlyAnomalies()]);
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
    const updatedHabits = habits.map(habit =>
      habit.name === habitName && !habit.isCompleted
        ? {
            ...habit,
            completed: habit.completed + 1,
            isCompleted: habit.completed + 1 >= habit.total,
          }
        : habit
    );

    const sorted = sortHabits(updatedHabits);
    setHabits(sorted);
  };

  const sortHabits = (list: HydratedHabit[]): HydratedHabit[] => {
    const incomplete = list.filter(h => !h.isCompleted);
    const complete = list.filter(h => h.isCompleted);

    incomplete.sort(
      (a, b) => (a.completed / a.total) - (b.completed / b.total)
    );

    return [...incomplete, ...complete];
  };

  const renderActiveHabits = (): JSX.Element => {

    return (
      <View style={styles.content}>
        <Text style={styles.statsTitle}>Habit Stats</Text>
        {/* Habit Stats */}
        <View style={styles.spikeCard}>
          {/* Habit count is hard coded for now */}
          <SpikeBar cardWidth={370} progress={anomalies} habitCount={3} />
        </View>

        {/* Habits for the week */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Habits for the week</Text>
          <Text style={styles.sectionSubtitle}>When you complete a habit, mark it as done!</Text>

          <View style={styles.habitsList}>
            {habits.map((habit, index) => (
              <HabitCard
                key={index}
                habit={habit}
                onToggle={() => toggleHabit(habit.name)}
              />
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
        ].map((dateRange, index) => (
          <RecapCard
            key={index}
            dateRange={dateRange}
            onPress={() => router.replace('/weekly-recap')}
          />
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
          onPress={() => router.replace('/home-screen')}
        >
          <HomeIcon />
          <Text style={styles.navText}>Home</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.navItem}>
          <GoalsIcon />
          <Text style={styles.navText}>Goals</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => router.replace('/progress')}
        >
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
  spikeCard: {
    marginBottom: 20
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
    gap: 4,
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