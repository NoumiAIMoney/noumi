import { colors, typography } from '@/src/theme';
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface CategoryVerticalCardProps {
  icon: React.ReactElement;
  label: string;
  iconBackground?: string;
  value?: string | React.ReactElement;
  valueIcon?: React.ReactElement;
}

export default function CategoryVerticalCard({ icon, label, iconBackground='#B4698F', value, valueIcon }: CategoryVerticalCardProps) {
  return (
    <View style={styles.card}>
      <View style={[styles.iconWrapper, { backgroundColor: iconBackground}]}>
        {icon}
      </View>
      {value && (
        <View style={styles.valueWrapper}>
          {valueIcon && <View style={styles.valueIcon}>{valueIcon}</View>}
          <Text style={styles.valueText}>{value}</Text>
        </View>
      )}
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: 90,
    minHeight: 110,
    borderRadius: 12,
    paddingTop: 12,
    paddingRight: 8,
    paddingBottom: 12,
    paddingLeft: 8,
    backgroundColor: colors.lightGrayBackground,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconWrapper: {
    width: 39.09,
    height: 40,
    padding: 10,
    borderRadius: 100,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  label: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.body,
    textAlign: 'center',
    color: colors.darkFont,
  },
  valueWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  valueIcon: {
    marginRight: 4,
  },
  valueText: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.small,
    color: colors.darkFont,
  },
});
