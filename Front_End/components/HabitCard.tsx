import { colors, shadows, typography } from '@/src/theme';
import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export type HabitData = {
  description: string;
  weekly_occurrences: number;
  completed?: number;
};

export type HydratedHabit = {
  name: string;
  prompt: string;
  total: number;
  completed: number;
  isCompleted: boolean;
};

export function hydrateHabits(habits: HabitData[]): HydratedHabit[] {
  return habits.map(habit => {
    const isNoumiHabit = habit.description.toLowerCase().includes('noumi');
    const total = habit.weekly_occurrences;
    const completed = isNoumiHabit ? total : habit.completed ?? 0;

    return {
      name: habit.description,
      prompt: habit.description,
      total,
      completed,
      isCompleted: completed >= total,
    };
  });
}

interface HabitCardProps {
  habit: HydratedHabit;
  onToggle: () => void;
}

const HabitCard: React.FC<HabitCardProps> = ({ habit, onToggle }) => {
  const progressPercent = (habit.completed / habit.total) * 100;

  return (
    <View style={styles.card}>
      <View style={styles.content}>
        <Text style={styles.text}>{habit.name}</Text>
        <View style={styles.progressWrapper}>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${progressPercent}%`,
                  backgroundColor: colors.progressBarOrange,
                },
              ]}
            />
          </View>
          <Text style={styles.progressText}>
            {habit.completed} out of {habit.total} complete
          </Text>
        </View>
      </View>

      <TouchableOpacity style={styles.checkButton} onPress={onToggle} disabled={habit.isCompleted}>
        {habit.isCompleted ? (
          <View style={styles.checked}>
            <Ionicons name="checkmark" size={16} color={colors.white} />
          </View>
        ) : (
          <View style={styles.unchecked} />
        )}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    elevation: 1,
    ...shadows.input
  },
  content: {
    flex: 1,
  },
  text: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.medium,
    color: colors.darkFont,
    marginBottom: 8,
  },
  progressWrapper: {
    gap: 4,
  },
  progressBar: {
    height: 10,
    backgroundColor: colors.progressBarOrangeLight,
    borderRadius: 6,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 6,
  },
  progressText: {
    fontSize: typography.fontSize.mini,
    color: colors.darkFont,
  },
  checkButton: {
    marginLeft: 12,
  },
  unchecked: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: colors.lightGrayFont,
  },
  checked: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.primaryGreen,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default HabitCard;
