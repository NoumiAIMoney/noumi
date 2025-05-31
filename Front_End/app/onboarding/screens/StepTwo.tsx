import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Keyboard,
  TouchableWithoutFeedback,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

import { colors, typography } from '@/src/theme';
import OptionCarousel from '@/components/OptionCarousel';
import Input from '@/components/Input';
import CalendarIcon from '../../../assets/icons/calendar.svg';
import DollarIcon from '../../../assets/icons/dollar.svg';
import { goalOptions } from '../../../lib/goalOptions';

interface StepTwoProps {
  selectedOptionId: string | null;
  onStepCompleted: (completed: boolean) => void;
  // onSelectOption: (id: string) => void;
}

export default function StepTwo({ selectedOptionId, onStepCompleted }: StepTwoProps) {
  const [goalName, setGoalName] = useState('');
  const [amount, setAmount] = useState('');
  const [targetDate, setTargetDate] = useState<Date | null>(null);
  const [showDatePicker, setShowDatePicker] = useState(false);

  const openTargetDatePicker = () => {
    setShowDatePicker(true);
  };

  const handleDateChange = (_event: any, selectedDate?: Date) => {
    setShowDatePicker(false);
    if (_event?.type === 'set' && selectedDate) {
      setTargetDate(selectedDate);
    }
  };

  useEffect(() => {
    const allFilled =
      !!selectedOptionId &&
      goalName.trim() !== '' &&
      amount.trim() !== '' &&
      targetDate !== null;
    onStepCompleted(allFilled);
  }, [selectedOptionId, goalName, amount, targetDate]);

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.text}>
          <Text style={styles.title}>Goal details</Text>
          <Text style={styles.subtitle}>Tell us more about your goal.</Text>
        </View>

        <View style={styles.form}>
          <View>
            <Text style={styles.label}>Your money goal</Text>
            <OptionCarousel
              options={goalOptions}
              selectedOptionId={selectedOptionId}
              onSelectOption={()=> {}}
            />
          </View>

          <Input
            label="Name your goal"
            mode="text"
            placeholder="What are you saving for?"
            value={goalName}
            onChangeText={setGoalName}
          />

          <Input
            label="Set the amount"
            keyboardType="numeric"
            mode="number"
            iconLeft={<DollarIcon width={30} height={30} stroke="#000" />}
            value={amount}
            onChangeText={setAmount}
          />
          {showDatePicker && (
            <View style={styles.pickerContainer}>
              <DateTimePicker
                value={targetDate || new Date()}
                mode="date"
                display="inline"
                onChange={handleDateChange}
              />
            </View>
          )}
          <Input
            label="Target Date"
            placeholder="dd/mm/yy"
            value={
              targetDate
                ? `${targetDate.getDate().toString().padStart(2, '0')}/${(targetDate.getMonth() + 1)
                    .toString()
                    .padStart(2, '0')}/${targetDate.getFullYear()}`
                : ''
            }
            onChangeText={() => {}}
            editable={false}
            iconRight={<CalendarIcon width={20} height={20} fill="#000" />}
            onPressIconRight={openTargetDatePicker}
            mode="date"
          />
        </View>
      </KeyboardAvoidingView>
    </TouchableWithoutFeedback>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    width: '100%',
  },
  text: {
    marginBottom: 20,
  },
  title: {
    fontSize: 20,
    fontFamily: typography.fontFamily.bold,
    marginBottom: 4,
    color: colors.black,
  },
  subtitle: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.regular,
    color: colors.gray,
    marginBottom: 20,
  },
  form: {
    gap: 24,
  },
  label: {
    marginBottom: 8,
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.body,
    color: colors.black,
  },
  pickerContainer: {
    position: 'absolute',
    bottom: 72,
    left: 0,
    right: 0,
    backgroundColor: '#fff',
    borderRadius: 8,
    zIndex: 10,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 5,
    width: 360,
    alignItems: 'center'
  }
});
