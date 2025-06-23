import { colors } from '@/src/theme';
import React from 'react';
import { StyleSheet, View } from 'react-native';

export default function DashBar({
  steps = 6,
  currentStep = 1,
  activeColor = colors.progressBarOrange,
  inactiveColor = colors.white,
  dashWidth = 45,
  dashHeight = 4,
}) {
  const dashes = Array.from({ length: steps });

  return (
    <View style={styles.container}>
      {dashes.map((_, index) => {
        const isActive = index + 1 === currentStep;
        return (
          <View
            key={index}
            style={[
              styles.dash,
              {
                width: dashWidth,
                height: dashHeight,
                backgroundColor: isActive ? activeColor : inactiveColor,
              },
            ]}
          />
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '90%'
  },
  dash: {
    borderRadius: 8,
  },
});
