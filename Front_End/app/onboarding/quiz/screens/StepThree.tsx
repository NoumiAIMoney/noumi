import Input from "@/components/Input";
import { colors, typography } from "@/src/theme";
import { useEffect } from "react";
import { Keyboard, StyleSheet, Text, TouchableWithoutFeedback, View } from "react-native";
import DollarIcon from '../../../../assets/icons/currency.svg';

interface StepThreeProps {
  onStepCompleted: (completed: boolean) => void;
  income: string | null;
  setIncome: (val: string) => void; 
}

export default function ({onStepCompleted, income, setIncome}: StepThreeProps) {

  useEffect(() => {
    onStepCompleted(income?.trim() !== '');
  }, [income]);

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={styles.container}>
        <View style={styles.text}>
          <Text style={styles.title}>Monthly Income</Text>
          <Text style={styles.subtitle}>Please include all your regular income.</Text>
        </View>
        <Input
          label="Your monthly income"
          keyboardType="numeric"
          mode="number"
          iconLeft={<DollarIcon width={24} height={24} stroke="#000" strokeWidth={0.5} />}
          value={income || ''}
          onChangeText={setIncome}
        />
      </View>
    </TouchableWithoutFeedback>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    width: '100%',
  },
  text: {
    marginBottom: 24,
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
})