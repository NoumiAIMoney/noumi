import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import PrimaryButton from '@/components/PrimaryButton';
import StepOne from './screens/StepOne';
import QuizProgressBar from '@/components/ProgressBar';
import StepTwo from './screens/StepTwo';
import { useRouter } from 'expo-router';

export default function QuizScreen() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [stepTwoCompleted, setStepTwoCompleted] = useState(false);
  const [selectionId, setSelectionId] = useState<string | null>(null);

  const handleContinue = () => {
    if (step === 1) {
      setStep(2);
      setStepTwoCompleted(false);
    } else if (step === 2 && stepTwoCompleted) {
      router.push('/plaid-connection');
    }
  };

  const handleSelectOption = (id: string) => {
    setSelectionId(id);
  };

  const currentStep = step;
  const totalSteps = 2;
  return (
    <View style={styles.container}>
      <QuizProgressBar currentStep={currentStep} totalSteps={totalSteps} />

      {step === 1 ? (
        <StepOne selectedOptionId={selectionId} onSelectOption={handleSelectOption} />
      ) : (
        <StepTwo
          selectedOptionId={selectionId}
          onStepCompleted={setStepTwoCompleted}
        />
      )}

      <PrimaryButton
        title="Continue"
        onPress={handleContinue}
        disabled={step === 1 ? !selectionId : !stepTwoCompleted}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingVertical: 24,
    paddingHorizontal: 12,
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  button: {
    marginTop: 16,
  },
});
