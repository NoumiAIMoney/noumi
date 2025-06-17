import React from 'react';
import { GestureResponderEvent, StyleSheet, Text, TouchableOpacity } from 'react-native';

import { colors, typography } from '../src/theme';

interface PrimaryButtonProps {
  title: string;
  onPress: (event: GestureResponderEvent) => void;
  disabled?: boolean;
}

export default function PrimaryButton({ title, onPress, disabled = false }: PrimaryButtonProps) {
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled}
      style={[styles.button, disabled ? styles.disabledButton : styles.enabledButton]}
    >
      <Text style={[styles.buttonText, { fontFamily: typography.fontFamily.semiBold }]}>
        {title}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    width: '80%',
    height: 56,
    borderRadius: 25,
    paddingVertical: 20,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
  },
  enabledButton: {
    backgroundColor: colors.primaryGreen,
  },
  disabledButton: {
    backgroundColor: colors.disabled,
  },
  buttonText: {
    fontFamily: typography.fontFamily.medium,
    color: '#FFFFFF',
    fontSize: typography.fontSize.body,
    lineHeight: 16,
    letterSpacing: 0,
  },
});
