import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { typography, colors } from '@/src/theme'; // adjust if needed

export default function SplashScreen() {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace('/onboarding');
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
    backgroundColor: '#593F90',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logo: {
    fontFamily: typography.fontFamily.madimi,
    color: '#fff',
    fontSize: typography.fontSize.extraLarge,
  },
});
