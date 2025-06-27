import OptionGrid from '@/components/OptionGrid';
import { colors, typography } from '@/src/theme';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { goalOptions } from '../../../../lib/goalOptions';

interface StepOneProps {
  selectedOption: string | null;
  onSelectOption: (label: string) => void;
}

export default function StepOne({ selectedOption, onSelectOption }: StepOneProps) {
  return (
    <View style={styles.container}>
      <View style={styles.text}>
        <Text style={styles.title}>Choose your money goal</Text>
        <Text style={styles.subtitle}>Select one that applies the most right now.</Text>
      </View>
      <OptionGrid
        options={goalOptions}
        selectedOption={selectedOption}
        onSelectOption={onSelectOption}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    width: '100%',
  },
  text: {
    marginBottom: 48,
  },
  title: {
    fontSize: 20,
    fontFamily: typography.fontFamily.bold,
    marginBottom: 4,
    color: colors.black,
  },
  subtitle: {
    fontSize: 16,
    fontFamily: typography.fontFamily.regular,
    color: colors.gray,
    marginBottom: 20,
  },
});
