import UncategorizedIcon from '@/assets/icons/categories/Uncategorized.svg';
import HorizontalCard from '@/components/HorizontalCard';
import PrimaryButton from '@/components/PrimaryButton';
import { getHabits } from '@/src/api/habits';
import { colors, typography } from '@/src/theme';
import { router } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface Habit {
  habit_description: string;
  occurrences: number;
  habit_full_prompt: string;
}

export default function Step5() {
  const [habits, setHabits] = useState<Habit[]>([]);
  useEffect(() => {
    async function fetchGoal() {
      try {
        const data = await getHabits();
        const filteredHabits = data.filter(
          (habit: { habit_description: string; }) => !/noumi/i.test(habit.habit_description)
        );

        setHabits(filteredHabits);
      } catch (error) {
        console.error('Failed to fetch habits:', error);
      }
    }
    fetchGoal();
  }, []);

  if (!habits) return null;

  return (
    <View style={styles.wrapper}>
      <View style={styles.container}>
        <Text style={styles.text}>You did great this week. Try these habits next and watch your funds grow.</Text>
        <View style={styles.cardsWrapper}>
          {habits.map((habit, index) => (
            <HorizontalCard
              key={index}
              title={habit.habit_full_prompt || 'N/A'}
              white={true}
              icon={
                <View style={styles.iconWrapper}>
                  <UncategorizedIcon width={24} height={24} fill="none" stroke={colors.white} />
                </View>
              }
              onlyLabel
            />
          ))}
        </View>
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
  wrapper: {
    flex: 1,
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: colors.greenBackground,
    paddingVertical: 32,
  },
  container: {
    flex: 1,
    backgroundColor: colors.greenBackground,
    paddingHorizontal: 20,
    paddingTop: 32,
  },
  text: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.darkFont,
    letterSpacing: 0,
    marginLeft: 8,
    marginBottom: 56,
    marginRight: 64
  },
  cardsWrapper: {
    alignItems: 'center',
  },
  iconWrapper: {
    width: 39.09,
    height: 40,
    padding: 10,
    borderRadius: 100,
    backgroundColor: '#B4698F',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonWrapper: {
    width: 400,
    alignItems: 'center'
  }
});