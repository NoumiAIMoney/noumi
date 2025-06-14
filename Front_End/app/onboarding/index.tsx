import ImageSlider from '@/components/ImageSlider';
import onboardingSlides from '@/lib/onboardingSlides';
import { colors, typography } from '@/src/theme';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function OnboardingScreen() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [stepTwoCompleted, setStepTwoCompleted] = useState(false);
  const [selectionId, setSelectionId] = useState<string | null>(null);

  const navigateToAuth = () => {
    router.replace('/auth-selection');
  };

  const navigateToLogin = () => {
    router.replace('/login');
  };

  return (
    <View style={styles.container}>
      <View>
        <View style={styles.text}>
          <Text style={styles.logo}>Noumi</Text>
          <Text style={styles.title}>Smarter Money Moves Start Here</Text>
          <Text style={styles.subtitle}>Track, plan and grow your money</Text>
        </View>
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
    backgroundColor: '#F5F5F8',
    paddingTop: 112,
    paddingBottom: 40,
    paddingHorizontal: 20,
  },
  text: {
    paddingBottom: 20
  },
  logo: {
    fontFamily: typography.fontFamily.madimi,
    fontSize: typography.fontSize.XLarge,
    color: colors.logo,
  },
  title: {
    fontFamily: typography.fontFamily.semiBold,
    marginTop: 10,
    fontSize: typography.fontSize.XXLarge,
    textAlign: 'left',
    lineHeight: 42,
    letterSpacing: typography.letterSpacing.normal,
    color: colors.black,
    width: '80%'
  },
  subtitle: {
    fontSize: typography.fontSize.body,
    color: colors.black,
    marginBottom: 20,
    textAlign: 'left',
    lineHeight: typography.lineHeight.body,
    fontFamily: typography.fontFamily.medium,
    marginTop: 10,
  },
  buttons: {
    gap: 12,
    marginTop: 'auto',
  },
  primaryBtn: {
    width: '80%',
    alignSelf: 'center',
    backgroundColor: colors.logo,
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
