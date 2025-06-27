import ImageSlider from '@/components/ImageSlider';
import onboardingSlides from '@/lib/onboardingSlides';
import { colors, typography } from '@/src/theme';
import { useRouter } from 'expo-router';
import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function OnboardingScreen() {
  const router = useRouter();

  const navigateToAuth = () => {
    router.replace('/auth-selection');
  };

  const navigateToLogin = () => {
    router.replace('/login');
  };

  return (
    <View style={styles.container}>
      <View>
        <Text style={styles.logo}>Noumi</Text>
        <ImageSlider slides={onboardingSlides} />
      </View>
      <View style={styles.buttons}>
        <TouchableOpacity 
          style={styles.primaryBtn} 
          onPress={navigateToAuth}
        >
          <Text style={styles.primaryText}>Get Started</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.secondaryBtn} 
          onPress={navigateToLogin}
        >
          <Text style={styles.link}>Log In</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.lightBackground,
    paddingTop: 112,
    paddingBottom: 40,
    paddingHorizontal: 20,
  },
  buttons: {
    gap: 12,
    marginTop: 'auto',
  },
  logo: {
    fontFamily: typography.fontFamily.madimi,
    fontSize: typography.fontSize.XLarge,
    color: colors.primaryGreen,
  },
  primaryBtn: {
    width: '80%',
    alignSelf: 'center',
    backgroundColor: colors.primaryGreen,
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 25,
    alignItems: 'center',
  },
  primaryText: {
    color: colors.white,
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.semiBold,
  },
  secondaryBtn: {
    width: '80%',
    alignSelf: 'center',
    backgroundColor: 'transparent',
    paddingVertical: 16,
    borderRadius: 25,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.black,
  },
  link: {
    fontSize: 16,
    color: colors.black,
    textAlign: 'center',
    fontWeight: '600',
  },
});
