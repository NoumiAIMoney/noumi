import OptionCard from '@/components/OptionCard';
import React, { ReactElement } from 'react';
import { StyleSheet, View } from 'react-native';

interface Option {
  id: string;
  label: string;
  icon: ReactElement;
}

interface Props {
  options: Option[];
  selectedOption: string | null;
  onSelectOption: (label: string) => void;
}

export default function OptionGrid({ options, selectedOption, onSelectOption }: Props) {

  return (
    <View style={styles.grid}>
      {options.map((option, index) => (
        <OptionCard
          key={index}
          label={option.label}
          icon={option.icon}
          selected={selectedOption === option.label}
          onPress={() => onSelectOption(option.label)}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  grid: {
    // TO DO: make dynamic to screen size of iPhone
    paddingLeft: 2,
    columnGap: 16,
    flexDirection: 'row',
    flexWrap: 'wrap',
    rowGap: 12,
  },
});
