import React, { ReactElement } from 'react';
import { View, StyleSheet } from 'react-native';
import OptionCard from '@/components/OptionCard';

interface Option {
  id: string;
  label: string;
  icon: ReactElement;
}

interface Props {
  options: Option[];
  selectedOptionId: string | null;
  onSelectOption: (label: string) => void;
  itemsPerRow: number;
}

export default function OptionGrid({ options, selectedOptionId, onSelectOption, itemsPerRow }: Props) {

  return (
    <View style={styles.grid}>
      {options.map((option, index) => (
        <OptionCard
          key={index}
          label={option.label}
          icon={option.icon}
          selected={selectedOptionId === option.id}
          onPress={() => onSelectOption(option.id)}
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
