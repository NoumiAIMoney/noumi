import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, typography } from '@/src/theme';
import ProgressBar from '@/components/ProgressBar';
import WeeklyStreak from './WeeklyStreak';

interface GoalProgressCardProps {
  title: string;
  daysLeft: string;
  amountSaved: string;
  goalAmount: string;
  percentage: string;
  streak?: boolean;
  height?: number;
  width?: number;
}

export default function GoalProgressCard({
  title,
  daysLeft,
  amountSaved,
  goalAmount,
  percentage,
  streak=false,
  height=126,
  width=332
}: GoalProgressCardProps) {
  return (
    <View style={[styles.card, {height, width}]}>
      <View style={styles.row}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.daysLeft}>{daysLeft}</Text>
      </View>

      <Text style={styles.amount}>
        <Text style={styles.amountSaved}>${amountSaved}</Text> of ${goalAmount}
      </Text>

      <View style={styles.row}>
        <Text style={styles.progressLabel}>Progress</Text>
        <Text style={styles.percentage}>{percentage}%</Text>
      </View>

      <ProgressBar currentStep={25} totalSteps={1200} width={340}/>
      {streak && <WeeklyStreak/>}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    padding: 16,
    backgroundColor: '#FCFCFC',
    borderColor: '#F1F1F1',
    borderWidth: 1,
    shadowColor: colors.darkFont,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 5,
    justifyContent: 'space-between',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8
  },
  title: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: 18,
    color: colors.darkFont,
  },
  daysLeft: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.mini,
    color: colors.darkFont,
  },
  amount: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.small,
    color: colors.darkFont,
    marginBottom: 8
  },
  amountSaved: {
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.large,
    color: colors.black,
  },
  progressLabel: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.mini,
    color: colors.darkFont,
  },
  percentage: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.mini,
    color: colors.darkFont,
  },
});
