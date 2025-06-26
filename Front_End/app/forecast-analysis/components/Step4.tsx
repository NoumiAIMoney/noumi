
import GoalProgressCard from '@/components/GoalProgressCard';
import { getComputedGoal } from '@/src/api/goal';
import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface GoalData {
  goal_name: string;
  target_date: string;
  goal_amount: number;
  amount_saved: number;
}

export default function Step4() {
  const [goal, setGoal] = useState<GoalData | null>(null);

  useEffect(() => {
    async function fetchGoal() {
      try {
        const data = await getComputedGoal();
        setGoal(data);
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

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Understanding your spending patterns is the first step.</Text>
      <Text style={styles.text}>Now, onto your action plan to get you closer to your goal!</Text>
      <View style={styles.section}>
        <GoalProgressCard
          title={goal.goal_name}
          daysLeft={`${daysLeft} days left`}
          amountSaved={String(goal.amount_saved)}
          goalAmount={goal.goal_amount.toLocaleString()}
          percentage={String(percentage)}
          barWidth={299}
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
    marginLeft: 8,
    marginBottom: 24,
    marginRight: 64
  },
  section: {
    alignItems: 'center',
    marginVertical: 16
  }
});
