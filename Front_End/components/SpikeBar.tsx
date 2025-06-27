import { colors, typography } from '@/src/theme';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

const MONTHS = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];

interface SpikeBarProps {
  progress: number[];
  habitCount?: number;
  width?: number;
}

export default function SpikeBar({ progress, habitCount, width=330 }: SpikeBarProps) {
  return (
    <View style={[styles.card, {width}]}>
      <View style={styles.row}>
        {habitCount !== undefined && (
          <View style={styles.habitCountSection}>
            <Text style={styles.habitCountText}>{habitCount}</Text>
            <Text style={styles.habitCountLabel}>Habits</Text>
            <Text style={styles.habitCountSubLabel}>This Year</Text>
          </View>
        )}

        <View style={styles.barsContainer}>
          {MONTHS.map((month, index) => {
            const fillRatio = Math.min(progress[index] / 12, 1);
            const filledHeight = 35 * fillRatio;

            return (
              <View key={index} style={styles.barWrapper}>
                <View style={styles.bar}>
                  <View
                    style={[
                      styles.barFill,
                      { height: filledHeight },
                    ]}
                  />
                </View>
                <Text style={styles.month}>{month}</Text>
              </View>
            );
          })}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    height: 103,
    borderRadius: 12,
    padding: 16,
    backgroundColor: colors.white,
    shadowColor: colors.darkFont,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 5,
    justifyContent: 'center',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  habitCountSection: {
    marginRight: 20,
    alignItems: 'flex-start',
  },
  habitCountText: {
    fontSize: 36,
    fontFamily: typography.fontFamily.bold,
    color: colors.primaryGreen,
    lineHeight: 40,
  },
  habitCountLabel: {
    fontSize: typography.fontSize.small,
    fontFamily: typography.fontFamily.semiBold,
    color: colors.primaryGreen,
  },
  habitCountSubLabel: {
    fontSize: typography.fontSize.mini,
    fontFamily: typography.fontFamily.semiBold,
    color: colors.grayFont,
  },
  barsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    flex: 1,
  },
  barWrapper: {
    alignItems: 'center',
  },
  bar: {
    width: 6,
    height: 35,
    borderRadius: 25,
    backgroundColor: colors.progressBarOrangeLight,
    overflow: 'hidden',
    justifyContent: 'flex-end',
  },
  barFill: {
    width: 6,
    backgroundColor: colors.progressBarOrange,
    borderRadius: 25,
  },
  month: {
    fontSize: typography.fontSize.mini,
    marginTop: 4,
    fontFamily: typography.fontFamily.bold,
    color: colors.grayFont,
  },
});
