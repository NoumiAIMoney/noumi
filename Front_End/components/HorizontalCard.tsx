import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, typography } from '@/src/theme';

interface HorizontalCardProps {
  title: string;
  amount?: string;
  white?: boolean;
  icon: React.ReactElement;
}

export default function HorizontalCard({
  title,
  amount,
  white = false,
  icon,
}: HorizontalCardProps) {
  const cardBackground = white ? colors.white : colors.lightGrayBackground;

  return (
    <View style={[styles.card, { backgroundColor: cardBackground }]}>
    <View style={styles.leftContent}>
      <View style={styles.icon}>{icon}</View>
      <View style={{ flex: 1 }}>
        <Text style={styles.title} numberOfLines={0}>{title}</Text>
      </View>
    </View>

      {amount && (
        <Text style={styles.amount}>
          ${amount}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: '100%',
    minHeight: 70,
    padding: 16,
    borderRadius: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  leftContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    marginRight: 12,
  },
  title: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.small,
    color: colors.black,
    flexWrap: 'wrap'
  },
  amount: {
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.large,
  },
});
