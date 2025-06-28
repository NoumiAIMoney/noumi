import { default as GoalsIcon, default as UncategorizedIcon } from '@/assets/icons/goals.svg';
import HomeIcon from '@/assets/icons/home.svg';
import IncomeIcon from '@/assets/icons/money-receive.svg';
import ExpenseIcon from '@/assets/icons/money-send.svg';
import ProgressIcon from '@/assets/icons/progress.svg';
import GoalProgressCard from '@/components/GoalProgressCard';
import { getComputedGoal } from '@/src/api/goal';
import { getHabits } from '@/src/api/habits';
import { getSpendingStatus } from '@/src/api/spending';
import { colors, typography } from '@/src/theme';
import { getCurrentWeekRange } from '@/src/utils/formatters';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

interface GoalData {
  goal_name: string;
  target_date: string;
  goal_amount: number;
  amount_saved: number;
}

interface SpendingData {
  income: number;
  expenses: number;
  amount_safe_to_spend: number;
}

interface HabitData {
  description: string;
  weekly_occurrences: number;
}

export default function HomeScreen() {
  const [goal, setGoal] = useState<GoalData | null>(null);
  const [spendingStatus, setSpendingStatus] = useState<SpendingData | null>(null);
  const [habits, setHabits] = useState<HabitData[]>([]);
  const [showAllHabits, setShowAllHabits] = useState(false);

  const habitsToDisplay = showAllHabits ? habits : habits.slice(0, 2);
  useEffect(() => {
    async function fetchGoal() {
      try {
        const [goalData, spendingData, habitData] = await Promise.all([
          getComputedGoal(),
          getSpendingStatus(),
          getHabits()
        ]);
        setGoal(goalData);
        setSpendingStatus(spendingData);
        setHabits(habitData.filter((h: { description: any; }) => h.description))
      } catch (error) {
        console.error('Failed to fetch goal:', error);
      }
    }
    fetchGoal();
  }, []);

  if (!goal) return null;

  const targetDate = new Date(goal.target_date);
  const today = new Date();
  const timeDiff = targetDate.getTime() - today.getTime();
  const daysLeft = Math.max(Math.ceil(timeDiff / (1000 * 3600 * 24)), 0);
  const percentage = Math.min(
    Math.round((goal.amount_saved / goal.goal_amount) * 100),
    100
  );
  const userName: string = "Maya";
  
  return (
    <LinearGradient
      colors={['#2E6B70', '#F3F5F5']}
      start={{ x: 0.5, y: 0 }}
      end={{ x: 0.5, y: 1 }}
      locations={[0.0001, 0.4489]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>M</Text>
            </View>
            <Text style={styles.greeting}>Good morning, {userName}</Text>
          </View>
          <TouchableOpacity style={styles.notificationBtn}>
            <Ionicons name="notifications-outline" size={24} color="#fff" />
          </TouchableOpacity>
        </View>

        {/* Goal Card */}
        <View style={styles.goalCard}>
          <GoalProgressCard
            title={goal.goal_name}
            daysLeft={`${daysLeft} days left`}
            amountSaved={String(goal.amount_saved)}
            goalAmount={goal.goal_amount.toLocaleString()}
            percentage={String(percentage)}
            streak
            height={191}
            width={373}
          />
        </View>

        {/* Weekly Recap Card */}
        <TouchableOpacity 
          style={styles.recapCard}
          onPress={() => router.replace('/weekly-recap')}
        >
          <View style={styles.recapContent}>
            <View style={styles.recapIcon}>
              <MaterialIcons name="emoji-events" size={24} color={colors.white} />
            </View>
            <View style={styles.recapText}>
              <Text style={styles.recapDate}>{getCurrentWeekRange()}</Text>
              <Text style={styles.recapTitle}>Your Weekly Recap</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={22} color={colors.black} marginLeft={-20}/>
        </TouchableOpacity>

        {/* My Spending Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>My Spending</Text>
            <TouchableOpacity>
              <Text style={styles.seeAllBtn}>See All</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.spendingRow}>
            <View style={styles.safeToSpendCard}>
              <Text style={styles.safeToSpendLabel}>Safe to Spend</Text>
              <Text style={styles.safeToSpendAmount}>
                {`$ ${spendingStatus?.amount_safe_to_spend.toLocaleString(undefined, {
                  minimumFractionDigits: 1,
                  maximumFractionDigits: 1,
                })}`}
              </Text>
              <Text style={styles.updateDate}>Updated: {new Date().toLocaleDateString('en-US')}</Text>
            </View>
            
            <View style={styles.summaryCards}>
              <View style={styles.summaryCard}>
                <View style={[styles.summaryIcon, { backgroundColor: colors.white }]}>
                  <IncomeIcon/>
                </View>
                <View>
                  <Text style={styles.summaryLabel}>Income</Text>
                  <Text style={styles.summaryAmount}>
                    {`$ ${spendingStatus?.income.toLocaleString(undefined, {
                      minimumFractionDigits: 1,
                      maximumFractionDigits: 1,
                    })}`}
                  </Text>
                </View>
              </View>
              
              <View style={styles.summaryCard}>
                <View style={[styles.summaryIcon, { backgroundColor: colors.white }]}>
                  <ExpenseIcon/>
                </View>
                <View>
                  <Text style={styles.summaryLabel}>Expenses</Text>
                  <Text style={styles.summaryAmount}>
                    {`$ ${spendingStatus?.expenses.toLocaleString(undefined, {
                      minimumFractionDigits: 1,
                      maximumFractionDigits: 1,
                    })}`}
                  </Text>
                </View>
              </View>
            </View>
          </View>
        </View>

        {/* My Habits Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>My Habits</Text>
            <TouchableOpacity onPress={() => setShowAllHabits(prev => !prev)}>
              <Text style={styles.seeAllBtn}>
                {showAllHabits ? 'See Less' : 'See All'}
              </Text>
            </TouchableOpacity>
          </View>
          {showAllHabits ? (
            <ScrollView
              style={{ maxHeight: 200 }}
              contentContainerStyle={{ paddingBottom: 32 }}
              showsVerticalScrollIndicator={false}
            >
              {habitsToDisplay.map((habit, index) => (
                <View key={index} style={styles.habitCard}>
                  <View
                    style={[
                      styles.habitIcon,
                      { backgroundColor: index % 2 === 0 ? '#608762' : '#B4698F' },
                    ]}
                  >
                    <UncategorizedIcon style={styles.habitIconImage} />
                  </View>
                  <Text style={styles.habitText}>{habit.description}</Text>
                </View>
              ))}
            </ScrollView>
          ) : (
            habitsToDisplay.map((habit, index) => (
              <View key={index} style={styles.habitCard}>
                <View
                  style={[
                    styles.habitIcon,
                    { backgroundColor: index % 2 === 0 ? '#608762' : '#B4698F' },
                  ]}
                >
                  <UncategorizedIcon style={styles.habitIconImage} />
                </View>
                <Text style={styles.habitText}>{habit.description}</Text>
              </View>
            ))
          )}
        </View>

        
        {/* Bottom Navigation */}
        <View style={styles.bottomNav}>
          <TouchableOpacity style={styles.navItem}>
            <HomeIcon/>
            <Text style={styles.navTextActive}>Home</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.navItem}>
            <GoalsIcon/>
            <Text style={styles.navText}>Goals</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.navItem} onPress={()=> router.replace('/progress')}>
            <ProgressIcon />
            <Text style={styles.navText}>Progress</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.large,
    color: colors.white,
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 12,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.progressBarOrange,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    color: colors.white,
    fontSize: 18,
    fontWeight: 'bold',
  },
  greeting: {
    color: colors.white,
    fontSize: typography.fontSize.large,
    fontFamily: typography.fontFamily.semiBold
  },
  notificationBtn: {
    padding: 8,
  },
  goalCard: {
    margin: 20,
    marginTop: 0,
  },
  recapCard: {
    backgroundColor: colors.white,
    marginHorizontal: 20,
    marginBottom: 16,
    height: 57,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  recapContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recapIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#377276',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  recapText: {
    flex: 1,
  },
  recapDate: {
    fontSize: typography.fontSize.mini,
    color: '#666',
    marginBottom: 2,
  },
  recapTitle: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.medium,
    color: colors.darkFont,
  },
  recapArrow: {
    marginLeft: 8,
    color: '#5E9B9C',
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: typography.fontSize.large,
    fontFamily: typography.fontFamily.semiBold,
    color: colors.darkFont,
  },
  seeAllBtn: {
    fontSize: typography.fontSize.small,
    color: '#489FCD',
    fontFamily: typography.fontFamily.medium,
  },
  spendingRow: {
    flexDirection: 'row',
    gap: 12,
  },
  safeToSpendCard: {
    flex: 1,
    backgroundColor: colors.greenBackground,
    borderRadius: 12,
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  safeToSpendLabel: {
    fontSize: typography.fontSize.small,
    color: colors.darkFont,
    fontFamily: typography.fontFamily.semiBold,
    marginBottom: 8,
  },
  safeToSpendAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.darkFont,
    marginBottom: 8,
  },
  updateDate: {
    fontSize: typography.fontSize.mini,
    color: '#666',
  },
  summaryCards: {
    flex: 1,
    gap: 12,
  },
  summaryCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  summaryIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.white,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  summaryLabel: {
    fontSize: typography.fontSize.mini,
    fontFamily: typography.fontFamily.regular,
    color: colors.black,
    marginBottom: 2,
  },
  summaryAmount: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.medium,
    color: colors.black,
  },
  habitCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  habitIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  habitIconImage: {
    // Add styles for the habit icon images if needed
  },
  habitText: {
    flex: 1,
    fontSize: typography.fontSize.small,
    color: '#333',
    lineHeight: 20,
  },
  bottomNav: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    backgroundColor: colors.white,
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: colors.lightGrayBackground,
  },
  navItem: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  navText: {
    fontSize: typography.fontSize.mini,
    color: '#999',
    marginTop: 4,
  },
  navTextActive: {
    fontSize: typography.fontSize.mini,
    color: '#000',
    marginTop: 4,
    fontWeight: '600',
  },
});