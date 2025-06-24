import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import HorizontalCard from '@/components/HorizontalCard';
import TrendUpIcon from '@/assets/icons/progress.svg'
import { getAccomplishedHabits } from '@/src/api/habits';

type Habit = {
  habit_description: string;
  value?: string;
}

export default function Step3() {
  const [accomplishments, setAccomplishments] = useState<Habit[] | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getAccomplishedHabits();

        setAccomplishments(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  if (!accomplishments) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.subtitle}>Habits</Text>
      <View style={styles.section}>
        {accomplishments.map((habit, index) => {
          const isNoumi = habit.value?.toLowerCase().includes('noumi');

          return (
            <HorizontalCard
              key={index}
              title={habit.habit_description || 'N/A'}
              white={true}
              width={330}
              iconRight={isNoumi}
              {...(
                isNoumi
                  ? { icon: <TrendUpIcon width={24} height={24} fill="none" /> }
                  : { amount: habit.value, amountColor: '#1BB16A' }
              )}
            />
          );
        })}
      </View>
      <Text style={styles.text}>Way to go! You're building new habits and they are paying off.</Text>
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
    marginLeft: 16,
    marginBottom: 24
  },
  section: {
    alignItems: 'center',
    marginBottom: 32
  },
  subtitle: {
    fontFamily: typography.fontFamily.medium,
    color: colors.darkFont,
    fontSize: typography.fontSize.body,
    marginVertical: 12,
    marginLeft: 16,
  },
});
