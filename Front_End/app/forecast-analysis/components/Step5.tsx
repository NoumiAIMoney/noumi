import UncategorizedIcon from '@/assets/icons/goals.svg';
import HorizontalCard from '@/components/HorizontalCard';
import { getHabits } from '@/src/api/habits';
import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface Habit {
  description: string;
  weekly_occurrences: number;
}

const COLORS = ['#B4698F', '#608762', '#5390D3']

export default function Step5() {
  const [habits, setHabits] = useState<Habit[]>([]);
  useEffect(() => {
    async function fetchGoal() {
      try {
        const data = await getHabits();
        setHabits(data);
      } catch (error) {
        console.error('Failed to fetch habits:', error);
      }
    }
    fetchGoal();
  }, []);

  if (!habits) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Try these habits to start saving more.</Text>
      <View style={styles.cardsWrapper}>
        {habits.slice(0, 3).map((habit, index) => (
          <HorizontalCard
            key={index}
            title={habit.description || 'N/A'}
            white={true}
            icon={
              <View style={[styles.iconWrapper, {backgroundColor: COLORS[index]}]}>
                <UncategorizedIcon width={24} height={24} fill="none" stroke={colors.white} />
              </View>
            }
            onlyLabel
          />
        ))}
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
  cardsWrapper: {
    alignItems: 'center',
  },
  iconWrapper: {
    width: 40,
    height: 40,
    padding: 10,
    borderRadius: 100,
    alignItems: 'center',
    justifyContent: 'center',
  },
});