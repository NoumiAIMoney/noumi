import PrimaryButton from '@/components/PrimaryButton';
import QuizProgressBar from '@/components/ProgressBar';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Alert, StyleSheet, View } from 'react-native';
import StepOne from './screens/StepOne';
import StepThree from './screens/StepThree';
import StepTwo from './screens/StepTwo';
import { submitQuiz } from '@/src/api/quiz';

type QuizData = {
  goal_name: string;
  goal_description: string;
  goal_amount: string;
  target_date: Date | null;
  net_monthly_income: string
};

export default function QuizScreen() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [stepTwoCompleted, setStepTwoCompleted] = useState(false);
  const [stepThreeCompleted, setStepThreeCompleted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [quizData, setQuizData] = useState<QuizData>({
    goal_name: '',
    goal_description: '',
    goal_amount: '',
    target_date: null,
    net_monthly_income: ''
  });

  const handleContinue = async () => {
    if (step === 1) {
      setStep(2);
      setStepTwoCompleted(false);
    } else if (step === 2 && stepTwoCompleted) {
      setStep(3);
    } else if (step === 3) {
      try {
        setIsLoading(true);
        await submitQuiz({
          goal_name: quizData.goal_name,
          goal_description: quizData.goal_description,
          goal_amount: Number(quizData.goal_amount.replace(/,/g, '')),
          target_date: quizData.target_date?.toISOString().split('T')[0] || '',
          net_monthly_income: Number(quizData.net_monthly_income.replace(/,/g, '')),
        });
        router.push('/plaid-connection');
      } catch (error) {
        Alert.alert('Error', 'Failed to submit quiz. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const currentStep = step;
  const totalSteps = 3;
  return (
    <View style={styles.container}>
      <QuizProgressBar currentStep={currentStep} totalSteps={totalSteps} />

      {step === 1 ? (
        <StepOne selectedOption={quizData.goal_name} onSelectOption={(label) => setQuizData((prev) => ({ ...prev, goal_name: label }))} />
      ) : step === 2 ? (
        <StepTwo
          selectedOption={quizData.goal_name}
          onStepCompleted={setStepTwoCompleted}
          onSelectOption={(label) => setQuizData((prev) => ({ ...prev, goal_name: label }))}
          goalAmount={quizData.goal_amount}
          setGoalAmount={(val) => setQuizData((prev) => ({ ...prev, goal_amount: val }))}
          goalDate={quizData.target_date}
          setGoalDate={(date) => setQuizData((prev) => ({ ...prev, target_date: date }))}
          goalDescription={quizData.goal_description}
          setGoalDescription={(val) => setQuizData((prev) => ({ ...prev, goal_description: val }))}
          />
      ) : (
        <StepThree 
          onStepCompleted={setStepThreeCompleted}
          income={quizData.net_monthly_income}
          setIncome={(income) => {setQuizData((prev) => ({ ...prev, net_monthly_income: income}))}}
        />
      )}

      <PrimaryButton
        title="Continue"
        onPress={handleContinue}
        disabled={
          (step === 1 && !quizData.goal_name) ||
          (step === 2 && !stepTwoCompleted) ||
          (step === 3 && !stepThreeCompleted)
        }
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
