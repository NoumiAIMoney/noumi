import React, { ReactElement } from 'react';
import { GestureResponderEvent, StyleSheet, Text, TouchableOpacity } from 'react-native';
import { colors, typography } from '../src/theme';

interface OptionCardProps {
  label: string;
  icon: ReactElement;
  selected?: boolean;
  onPress?: (event: GestureResponderEvent) => void;
}

export default function OptionCard({ label, icon, selected = false, onPress }: OptionCardProps) {
  return (
    <TouchableOpacity onPress={onPress} style={[styles.card, selected && styles.selectedCard]}>
      {icon}
      <Text style={styles.label}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    width: 108,
    height: 115,
    borderRadius: 15,
    backgroundColor: colors.white,
    padding: 8,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  selectedCard: {
    borderWidth: 2,
    borderColor: colors.primaryGreen,
  },
  label: {
    textAlign: 'center',
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.body,
    color: colors.darkFont,
    maxWidth: 88,
  },
});
