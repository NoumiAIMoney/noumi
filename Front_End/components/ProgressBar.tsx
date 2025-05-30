import React from 'react';
import { View, StyleSheet } from 'react-native';

import { colors } from '../src/theme';

interface QuizProgressBarProps {
  currentStep: number;
  totalSteps: number;
}

const QuizProgressBar: React.FC<QuizProgressBarProps> = ({ currentStep, totalSteps }) => {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <View style={styles.wrapper}>
      <View style={[styles.filler, { width: `${progress}%` }]} />
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    height: 8,
    width: '80%',
    backgroundColor: colors.lightPurple,
    borderRadius: 6,
    overflow: 'hidden',
    marginBottom: 24,
  },
  filler: {
    height: '100%',
    backgroundColor: colors.primaryPurple,
    borderRadius: 6,
  },
});

export default QuizProgressBar;
