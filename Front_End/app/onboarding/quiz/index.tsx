import PrimaryButton from '@/components/PrimaryButton';
import QuizProgressBar from '@/components/ProgressBar';
import { api } from '@/services/api';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Alert, StyleSheet, View } from 'react-native';
import StepOne from './screens/StepOne';
import StepTwo from './screens/StepTwo';

export default function QuizScreen() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [stepTwoCompleted, setStepTwoCompleted] = useState(false);
  const [selectionId, setSelectionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleContinue = async () => {
    if (step === 1) {
      setStep(2);
      setStepTwoCompleted(false);
    } else if (step === 2 && stepTwoCompleted) {
      try {
        setIsLoading(true);
        // Submit quiz data
        await api.submitQuiz({
          user_id: 'temp-user-id', // Replace with actual user ID from auth
          answers: {
            stepOne: selectionId,
            stepTwo: stepTwoCompleted
          }
        });
        router.push('/plaid-connection');
      } catch (error) {
        Alert.alert('Error', 'Failed to submit quiz. Please try again.');
      } finally {
        setIsLoading(false);
      }
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
        // TO DO: ADD LOADING WHEN NEEDED
        // loading={isLoading}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 80,
    paddingBottom: 40,
    paddingHorizontal: 12,
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  button: {
    marginTop: 16,
  },
});
