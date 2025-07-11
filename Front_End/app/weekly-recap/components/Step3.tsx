import TrendUpIcon from '@/assets/icons/progress.svg';
import HorizontalCard from '@/components/HorizontalCard';
import { getAccomplishedHabits } from '@/src/api/habits';
import { colors, typography } from '@/src/theme';
import { formatDollarAmountsInText } from '@/src/utils/formatters';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

type Habit = {
  description: string;
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
              title={formatDollarAmountsInText(habit.description) || 'N/A'}
              white={true}
              width={330}
              iconRight={isNoumi}
              {...(
                isNoumi
                  ? { icon: <TrendUpIcon width={24} height={24} fill="none" /> }
                  : { amount: habit.value, amountColor: '#1BB16A' }
              )}
              withShadow
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
    width: 350,
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.darkFont,
    letterSpacing: 0,
    marginLeft: 32,
    marginBottom: 24,
    marginRight: 24
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
    marginLeft: 32,
  },
});
