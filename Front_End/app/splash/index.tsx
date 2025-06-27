import { colors, typography } from '@/src/theme';
import { useRouter } from 'expo-router';
import React, { useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';

export default function SplashScreen() {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => {
      // UNCOMMENT
      router.replace('/onboarding');

      // TESTING SCREENS FAST
      // router.replace('/home-screen');
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>Noumi</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.white,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logo: {
    fontFamily: typography.fontFamily.madimi,
    color: colors.primaryGreen,
    fontSize: typography.fontSize.XXXLarge,
  },
});
