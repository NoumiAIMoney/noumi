
import GoalProgressCard from '@/components/GoalProgressCard';
import PrimaryButton from '@/components/PrimaryButton';
import { getComputedGoal } from '@/src/api/goal';
import { getWeeklySavings } from '@/src/api/savings';
import { colors, typography } from '@/src/theme';
import { router } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface GoalData {
  goal_name: string;
  target_date: string;
  goal_amount: number;
  amount_saved: number;
}

export default function Step6() {
  const [goal, setGoal] = useState<GoalData | null>(null);
  const [suggestedSavingsAmount, setSuggestedSavingsAmount] = useState<Number | null>(null);

  useEffect(() => {
    async function fetchGoal() {
      try {
        const [goalData, savingsData] = await Promise.all([
                  getComputedGoal(),
                  getWeeklySavings(),
                ]);
        setGoal(goalData);
        setSuggestedSavingsAmount(savingsData.suggested_savings_amount_weekly);
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
  const daysLeft = Math.max(Math.ceil(timeDiff / (1000 * 3600 * 24)) - 7, 0);
  const percentage = Math.min(
    Math.round((Number(suggestedSavingsAmount) / goal.goal_amount) * 100),
    100
  );

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Stay consistent with these habits and your goal could look like this next week.</Text>
      <View style={styles.section}>
        <GoalProgressCard
          title={goal.goal_name}
          daysLeft={`${daysLeft} days left`}
          // no savings + suggested amount
          amountSaved={String(0 + Number(suggestedSavingsAmount))}
          goalAmount={goal.goal_amount.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
          percentage={String(percentage)}
          barWidth={299}
        />
      </View>
      <View style={styles.buttonWrapper}>
        <PrimaryButton
          title="Home Page"
          onPress={() => router.push('/home-screen')}
        />
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
  text: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.darkFont,
    letterSpacing: 0,
    marginLeft: 32,
    marginBottom: 24,
    marginRight: 72
  },
  section: {
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 300
  },
  buttonWrapper: {
    width: 400,
    alignItems: 'center'
  }
});
