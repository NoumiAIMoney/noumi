import { colors, typography } from '@/src/theme';
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const MONTHS = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];

interface SpikeBarProps {
  progress: number[];
}

export default function SpikeBar({ progress }: SpikeBarProps) {
  return (
    <View style={styles.card}>
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
  );
}

const styles = StyleSheet.create({
  card: {
    width: 321,
    height: 103,
    gap: 16,
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
  barsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
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
    color: colors.grayFont
  },
});
