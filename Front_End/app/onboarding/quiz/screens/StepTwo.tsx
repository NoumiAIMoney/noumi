import DateTimePicker from '@react-native-community/datetimepicker';
import React, { useEffect, useState } from 'react';
import {
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TouchableWithoutFeedback,
  View,
} from 'react-native';

import Input from '@/components/Input';
import OptionCarousel from '@/components/OptionCarousel';
import { colors, typography } from '@/src/theme';
import CalendarIcon from '../../../../assets/icons/calendar.svg';
import DollarIcon from '../../../../assets/icons/currency.svg';
import { goalOptions } from '../../../../lib/goalOptions';

interface StepTwoProps {
  selectedOption: string | null;
  onStepCompleted: (completed: boolean) => void;
  onSelectOption: (label: string) => void;
  goalDescription: string | null;
  setGoalDescription: (val: string) => void;
  goalAmount: string | null;
  setGoalAmount: (val: string) => void;
  goalDate: Date | null;
  setGoalDate: (date: Date) => void;
}

export default function StepTwo({ selectedOption, onStepCompleted, onSelectOption, goalDescription, setGoalDescription, goalAmount, setGoalAmount, goalDate, setGoalDate }: StepTwoProps) {
  const [showDatePicker, setShowDatePicker] = useState(false);

  const openTargetDatePicker = () => {
    setShowDatePicker(true);
  };

  const handleDateChange = (_event: any, selectedDate?: Date) => {
    setShowDatePicker(false);
    if (_event?.type === 'set' && selectedDate) {
      setGoalDate(selectedDate);
    }
  };

  useEffect(() => {
    const allFilled =
      !!selectedOption &&
      goalDescription?.trim() !== '' &&
      goalAmount?.trim() !== '' &&
      goalDate !== null;
    onStepCompleted(allFilled);
  }, [selectedOption, goalDescription, goalAmount, goalDate]);

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
              selectedOption={selectedOption}
              onSelectOption={onSelectOption}
            />
          </View>

          <Input
            label="Name your goal"
            mode="text"
            placeholder="What are you saving for?"
            value={goalDescription || ''}
            onChangeText={setGoalDescription}
          />

          <Input
            label="Set the amount"
            keyboardType="numeric"
            mode="number"
            iconLeft={<DollarIcon width={24} height={24} stroke="#000" strokeWidth={0.5} />}
            value={goalAmount || ''}
            onChangeText={setGoalAmount}
          />
          {showDatePicker && (
            <View style={styles.pickerContainer}>
              <DateTimePicker
                value={goalDate || new Date()}
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
              goalDate
                ? `${goalDate.getDate().toString().padStart(2, '0')}/${(goalDate.getMonth() + 1)
                    .toString()
                    .padStart(2, '0')}/${goalDate.getFullYear()}`
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
