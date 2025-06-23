import { colors, typography } from '@/src/theme';
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface CategoryVerticalCardProps {
  icon: React.ReactElement;
  label: string;
}

export default function CategoryVerticalCard({ icon, label }: CategoryVerticalCardProps) {
  return (
    <View style={styles.card}>
      <View style={styles.iconWrapper}>
        {icon}
      </View>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: 90,
    height: 110,
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
    backgroundColor: '#B4698F',
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
});
