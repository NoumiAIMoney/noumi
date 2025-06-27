import { colors, typography } from '@/src/theme';
import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  TextInput,
  TextInputProps,
  TouchableOpacity,
  View,
} from 'react-native';

interface InputProps extends TextInputProps {
  label: string;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  onPressIconRight?: () => void;
  mode?: 'text' | 'number' | 'date';
}

export default function Input({
  label,
  iconLeft,
  iconRight,
  onPressIconRight,
  mode = 'text',
  style,
  ...textInputProps
}: InputProps) {
  const [inputFocused, setInputFocused] = useState(false);
  const handleChangeText = (text: string) => {
    if (mode === 'number') {
      const numeric = text.replace(/[^0-9]/g, '');
      const formatted = new Intl.NumberFormat().format(Number(numeric || 0));
      textInputProps.onChangeText?.(formatted);
    } else {
      textInputProps.onChangeText?.(text);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>

      <TouchableOpacity
        style={[styles.inputWrapper, inputFocused && styles.inputFocused]}
        activeOpacity={mode === 'date' ? 0.7 : 1}
        onPress={mode === 'date' ? onPressIconRight : undefined}
      >
        {iconLeft && <View style={styles.iconLeft}>{iconLeft}</View>}
        <TextInput
          {...textInputProps}
          editable={mode !== 'date'}
          style={[
            styles.input,
            style,
            iconLeft ? { paddingLeft: 40 } : null,
            iconRight ? { paddingRight: 40 } : null,
            textInputProps.value ? { color: colors.black } : null,
          ]}
          value={textInputProps.value}
          onChangeText={handleChangeText}
          keyboardType={mode === 'number' ? 'numeric' : 'default'}
          placeholderTextColor={colors.lightGrayFont}
          pointerEvents={mode === 'date' ? 'none' : 'auto'}
          onFocus={() => setInputFocused(true)}
          onBlur={() => setInputFocused(false)}
        />
        {iconRight && (
          <TouchableOpacity onPress={onPressIconRight} style={styles.iconRight}>
            {iconRight}
          </TouchableOpacity>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
    marginBottom: 16,
    position: 'relative',
  },
  label: {
    marginBottom: 6,
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.body,
    color: colors.black,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 8,
    backgroundColor: '#fff',
    height: 50,
    paddingLeft: 16,
    paddingRight: 8,
    position: 'relative',
  },
  input: {
    flex: 1,
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.regular,
    justifyContent: 'center',
  },
  iconLeft: {
    position: 'absolute',
    left: 10,
    top: '50%',
    transform: [{ translateY: -12 }],
    zIndex: 1,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconRight: {
    position: 'absolute',
    right: 10,
    top: '50%',
    transform: [{ translateY: -12 }],
    zIndex: 1,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  inputFocused: {
    borderColor: colors.primaryGreen,
    borderWidth: 1,
    shadowColor: '#00014',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 4,
  },
});
