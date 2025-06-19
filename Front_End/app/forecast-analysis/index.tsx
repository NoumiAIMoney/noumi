import DashBar from '@/components/DashBar';
import { colors } from '@/src/theme';
import React, { useState } from 'react';
import { StyleSheet, TouchableWithoutFeedback, View } from 'react-native';
import Step1 from './components/Step1';
import Step2 from './components/Step2';
import Step3 from './components/Step3';
import Step4 from './components/Step4';
import Step5 from './components/Step5';
import Step6 from './components/Step6';

const TOTAL_STEPS = 6;
const steps = [Step1, Step2, Step3, Step4, Step5, Step6];

export default function ForecastAnalysis() {
  const [currentStep, setCurrentStep] = useState(1);

  const goToStep = (step: number) => {
    if (step >= 1 && step <= TOTAL_STEPS) {
      setCurrentStep(step);
    }
  };

  const CurrentStepComponent = steps[currentStep - 1];
  return (
    <View style={styles.container}>
      <DashBar currentStep={currentStep} steps={TOTAL_STEPS} />

      <CurrentStepComponent />

      <TouchableWithoutFeedback onPress={() => goToStep(currentStep - 1)}>
        <View style={[styles.tapZone, { left: 0, width: 100 }]} />
      </TouchableWithoutFeedback>

      <TouchableWithoutFeedback onPress={() => goToStep(currentStep + 1)}>
        <View style={[styles.tapZone, { right: 0, width: 120 }]} />
      </TouchableWithoutFeedback>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.greenBackground,
    paddingVertical: 80,
    alignItems: 'center',
    justifyContent: 'flex-start',
  },
  text: {
    marginTop: 40,
    fontSize: 22,
    color: '#fff',
  },
  tapZone: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    zIndex: 10,
  },
});
