import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import FireIcon from '@/assets/icons/fire.svg';
import { getWeeklyStreak } from '@/src/api/streak';
import { colors, typography } from '@/src/theme';

export default function WeeklyStreak() {
  const [streak, setStreak] = useState<number[]>([]);

  useEffect(() => {
    async function fetchStreak() {
      try {
        const data = await getWeeklyStreak();
        setStreak(data);
      } catch (err) {
        console.error('Failed to fetch streak:', err);
      }
    }
    fetchStreak();
  }, []);

  const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

  return (
    <View style={styles.weeklyCalendar}>
      {days.map((day, index) => (
        <View key={index} style={styles.dayContainer}>
          <Text style={styles.dayLabel}>{day}</Text>
          <View style={styles.dayCircle}>
            {streak[index] ? (
              <FireIcon width={18} height={18} />
            ) : (
              <View style={styles.emptyDay} />
            )}
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  weeklyCalendar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#EEF2F5',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    alignItems: 'center',
  },
  dayContainer: {
    alignItems: 'center',
    flex: 1,
    height: 30,
  },
  dayLabel: {
    fontSize: typography.fontSize.mini,
    fontFamily: typography.fontFamily.semiBold,
    color: colors.darkFont,
    marginBottom: 8,
    height: 15,
    marginTop: -2,
  },
  dayCircle: {
    width: 20,
    height: 8,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyDay: {
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#D1D5DB',
  },
});
