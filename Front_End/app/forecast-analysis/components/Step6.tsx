import SparkleIcon from '@/assets/icons/sparkle.svg';
import { colors, typography } from '@/src/theme';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export default function Step6() {
  return (
    <View style={styles.container}>
      <SparkleIcon
        width={80}
        height={80}
        stroke={colors.primaryGreen}
        fill={colors.primaryGreen}
        strokeWidth={1}
      />
      <Text style={styles.text}>Step 6</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.lightBackground,
    paddingHorizontal: 20,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 24
  },
  text: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.body,
    color: colors.darkFont,
    lineHeight: typography.lineHeight.body
  }
});
