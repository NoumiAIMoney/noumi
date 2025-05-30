import React, { ReactElement, useEffect, useRef } from 'react';
import { ScrollView, StyleSheet, Dimensions, View } from 'react-native';
import OptionCard from '@/components/OptionCard';

interface Option {
  id: string;
  label: string;
  icon: ReactElement;
}

interface Props {
  options: Option[];
  selectedOptionId: string | null;
  onSelectOption: (id: string) => void;
}

export default function OptionCarousel({ options, selectedOptionId, onSelectOption }: Props) {
  const scrollViewRef = useRef<ScrollView>(null);
  const cardWidth = (Dimensions.get('window').width - 86) / 3;
  const gap = 12;

  useEffect(() => {
    if (selectedOptionId && scrollViewRef.current) {
      const selectedIndex = options.findIndex((o) => o.id === selectedOptionId);
      if (selectedIndex !== -1) {
        const maxIndex = options.length - 3;
        let scrollIndex = selectedIndex - 1;
        if (scrollIndex < 0) scrollIndex = 0;
        if (scrollIndex > maxIndex) scrollIndex = maxIndex;

        const offset = scrollIndex * (cardWidth + gap);

        scrollViewRef.current.scrollTo({ x: offset, animated: false });
      }
    }
  }, [selectedOptionId, options]);

  return (
    <ScrollView
      ref={scrollViewRef}
      horizontal
      showsHorizontalScrollIndicator={true}
      contentContainerStyle={styles.scroll}
      snapToInterval={cardWidth + gap}
      decelerationRate="fast"
      pagingEnabled={false}
    >
      {options.map((option) => (
        <View key={option.id} style={{ width: cardWidth }}>
          <OptionCard
            label={option.label}
            icon={option.icon}
            selected={selectedOptionId === option.id}
            onPress={() => onSelectOption(option.id)}
          />
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: {
    flexDirection: 'row',
    gap: 11,
  },
});
