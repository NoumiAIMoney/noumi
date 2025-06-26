import ArrowDownIcon from '@/assets/icons/Arrow_left.svg';
import TrendUpIcon from '@/assets/icons/progress.svg';
import { categoryIcons } from '@/components/CategoryIcons';
import CategoryVerticalCard from '@/components/CategoryVerticalCard';
import ProgressBar from '@/components/ProgressBar';
import { getComputedGoal } from '@/src/api/goal';
import { getWeeklySavings } from '@/src/api/savings';
import { getSpendingCategories, getTotalSpending } from '@/src/api/spending';
import { getLongestStreak } from '@/src/api/streak';
import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface GoalData {
  goal_name: string;
  target_date: string;
  goal_amount: number;
  amount_saved: number;
}

function getCategoryWithHighestDecrease(data: { category_name: string; amount: number; month: string; }[]) {
  const grouped: Record<string, { [month: string]: number }> = {};

  data.forEach(({ category_name, amount, month }) => {
    if (!grouped[category_name]) grouped[category_name] = {};
    grouped[category_name][month] = amount;
  });

  let maxDrop = -Infinity;
  let result: { category: string; decreaseAmount: number; percentageDrop: number } | null = null;

  for (const [category, months] of Object.entries(grouped)) {
    const monthEntries = Object.entries(months).sort(([a], [b]) => a.localeCompare(b));
    if (monthEntries.length < 2) continue;

    const [prevMonth, prevAmount] = monthEntries[0];
    const [currMonth, currAmount] = monthEntries[1];
    const drop = prevAmount - currAmount;

    if (drop > maxDrop) {
      maxDrop = drop;
      const percentageDrop = (drop / prevAmount) * 100;
      result = {
        category,
        decreaseAmount: parseFloat(drop.toFixed(2)),
        percentageDrop: parseFloat(percentageDrop.toFixed(2)),
      };
    }
  }

  return result;
}

export default function Step1() {
  const [goal, setGoal] = useState<GoalData | null>(null);
  const [suggestedSavingsAmount, setSuggestedSavingsAmount] = useState<number | null>(null);
  const [biggestDecrease, setBiggestDecrease] = useState<{
    category: string;
    decreaseAmount: number;
    percentageDrop: number;
  } | null>(null);
  const [streak, setStreak] = useState<Number[]>([]);
  const [totalSpending, setTotalSpending] = useState<Number>();

  useEffect(() => {
    async function fetchData() {
      try {
        const [goalData, savingsData, spendingCategories, streakData, spendingData] = await Promise.all([
          getComputedGoal(),
          getWeeklySavings(),
          getSpendingCategories(),
          getLongestStreak(),
          getTotalSpending(),
        ]);

        setGoal(goalData);
        setSuggestedSavingsAmount(savingsData.suggested_savings_amount_weekly);

        const result = getCategoryWithHighestDecrease(spendingCategories);
        setBiggestDecrease(result);
        setStreak(streakData.longest_streak);
        setTotalSpending(spendingData.spent_so_far);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    }

    fetchData();
  }, []);


  if (!goal) return null;

  const percentage = Math.min(
    Math.round((goal.amount_saved / goal.goal_amount) * 100),
    100
  );

  return (
    <View style={styles.container}>
      <View style={styles.textGroup}>
        <Text style={styles.date}>05/26 - 05/31</Text>
        <Text style={styles.titleWeekly}>Weekly Recap</Text>
      </View>
      <View style={styles.cardWrapper}>
        <View style={styles.avatar}><Text style={styles.initial}>M</Text></ View>
        <View style={styles.card}>
          <Text style={styles.mainTitle}>You are on a roll, Maya!</Text>
          <Text style={styles.subtitle}>This week's savings</Text>
          <Text style={styles.amount}>${Math.floor(suggestedSavingsAmount || 0)}</Text>
          <Text style={styles.subtitle}>Goal progress</Text>
          <Text style={styles.percentage}>{percentage}%</Text>
          <ProgressBar currentStep={goal.amount_saved} totalSteps={goal.goal_amount} width={202} />
          <Text style={styles.subtitle}>Your Weekly Stats</Text>
          <View style={styles.horizontalCardContainer}>
            <CategoryVerticalCard
              icon={categoryIcons[biggestDecrease?.category || 'Uncategorized'] || categoryIcons['Uncategorized']}
              label={biggestDecrease?.category || ''}
              valueIcon={<ArrowDownIcon width={12} height={12} stroke="green" />}
              value={`${biggestDecrease?.percentageDrop}%` || ''}
              iconBackground='#9C5538'
            />
            <CategoryVerticalCard
              icon={<TrendUpIcon width={24} height={24} fill="none" />}
              label='Longest Streak'
              iconBackground='#FFCE51'
              value={`${streak} Days`}
            />
            <CategoryVerticalCard
              icon={<TrendUpIcon width={24} height={24} fill="none" />}
              label='Money Spent'
              iconBackground='#5390D3'
              value={`$${totalSpending}`}
            />
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.greenBackground,
    paddingHorizontal: 20,
    paddingTop: 64
  },
  textGroup: {
    alignItems: 'flex-end'
  },
  date: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.body,
    color: colors.lighterFont,
    lineHeight: typography.lineHeight.body
  },
  titleWeekly: {
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.lighterFont,
    lineHeight: typography.lineHeight.XXLarge
  },
  cardWrapper: {
    position: 'relative',
    marginTop: 8,
    alignSelf: 'flex-start',
    marginLeft: 0,
  },
  avatar: {
    position: 'absolute',
    top: -25,
    left: 18,
    width: 50,
    height: 50,
    borderRadius: 50,
    backgroundColor: colors.progressBarOrange,
    paddingVertical: 12,
    paddingHorizontal: 14,
    zIndex: 2,
  },
  initial: {
    color: colors.white,
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XLarge
  },
  card: {
    width: 353,
    height: 543,
    borderRadius: 16,
    backgroundColor: colors.white,
    paddingTop: 40,
    paddingRight: 16,
    paddingBottom: 40,
    paddingLeft: 16,
    shadowColor: '#191919',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 8,
    zIndex: 1,
  },
  mainTitle: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XLarge,
    color: colors.darkFont,
    marginBottom: 16
  },
  subtitle: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.large,
    lineHeight: typography.lineHeight.body,
    color: colors.darkFont,
    marginTop: 16,
    marginBottom: 8
  },
  percentage: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.large,
    lineHeight: typography.lineHeight.body,
    color: colors.darkFont,
    marginTop: 8
  },
  amount: {
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.XXXXLarge,
    lineHeight: typography.lineHeight.XXLarge,
    color: colors.black,
    marginBottom: 16
  },
  horizontalCardContainer: {
    flexDirection: 'row',
    gap: 24,
    marginTop: 8,
  }
});
