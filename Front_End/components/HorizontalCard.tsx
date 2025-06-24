import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, typography } from '@/src/theme';

interface HorizontalCardProps {
  title: string;
  amount?: string;
  white?: boolean;
  icon: React.ReactElement;
  width?: number;
  onlyLabel?: boolean,
  amountColor?: string;
}

export default function HorizontalCard({
  title,
  amount,
  white = false,
  icon,
  width = 362,
  onlyLabel = false,
  amountColor = colors.blueFont
}: HorizontalCardProps) {
  const cardBackground = white ? colors.white : colors.lightGrayBackground;

  return (
    <View style={[styles.card, { backgroundColor: cardBackground, width }]}>
      <View style={styles.leftContent}>
        <View style={styles.icon}>{icon}</View>
        <View style={[styles.textWrapper, !amount && { maxWidth: '100%' }]}>
          <Text style={[styles.title, onlyLabel
            ? { fontFamily: typography.fontFamily.medium }
            : { fontFamily: typography.fontFamily.regular }
            ]} numberOfLines={2}
          >
            {title}
          </Text>
        </View>
      </View>

      {amount && (
        <Text style={[styles.amount, {color: amountColor}]}>
          ${amount}
        </Text>
      )}
    </View>
  );
}


const styles = StyleSheet.create({
  card: {
    height: 70,
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
    flex: 1,
  },
  icon: {
    marginRight: 12,
  },
  textWrapper: {
    flexShrink: 1,
    flexGrow: 1,
    flexBasis: 0,
  },
  title: {
    fontSize: typography.fontSize.small,
    color: colors.black,
    flexWrap: 'wrap',
  },
  amount: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.body,
    textAlign: 'right'
  },
});

