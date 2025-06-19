import { colors, typography } from '@/src/theme';
import { router } from 'expo-router';
import React, { useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import SparkleIcon from '../../assets/icons/sparkle.svg';

export default function Forecast() {
  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace('/forecast-analysis');
    }, 5000);
    return () => clearTimeout(timer);
  }, []);
  return (
    <View style={styles.container}>
      <SparkleIcon
        width={80}
        height={80}
        stroke={colors.primaryGreen}
        fill={colors.primaryGreen}
        strokeWidth={1}
      />
      <Text style={styles.text}>Generating your plan...</Text>
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
