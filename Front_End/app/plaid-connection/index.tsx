import PrimaryButton from '@/components/PrimaryButton';
import { colors, shadows, typography } from '@/src/theme';
import React from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';
import LightningIcon from '../../assets/icons/lightning.svg';
import ShieldIcon from '../../assets/icons/shield.svg';
import SparkleIcon from '../../assets/icons/sparkle.svg';

export default function QuizScreen() {
  return (
    <View style={styles.container}>
      <Image
        source={require('@/assets/images/logos.png')}
        style={styles.logos}
        resizeMode="contain"
      />
      <Text style={styles.title}><Text style={styles.noumiText}>Noumi</Text> uses <Text style={styles.plaidText}>Plaid</Text> to connect your account</Text>
      <View style={styles.features}>
        <View style={styles.featureContainer}>
          <SparkleIcon
            width={20}
            height={20}
            stroke={colors.darkFont}
            strokeWidth={1}
          />
          <View style={styles.featureTextContainer}>
            <Text style={styles.featureTitle}>Unlock the power of AI</Text>
            <Text style={styles.featureText}>Noumi works best if you connect all your bank accounts</Text>
          </View>
        </View>
        <View style={styles.featureContainer}>
          <LightningIcon
            width={20}
            height={20}
            stroke={colors.darkFont}
            strokeWidth={1}
          />
          <View style={styles.featureTextContainer}>
            <Text style={styles.featureTitle}>Connect in seconds</Text>
            <Text style={styles.featureText}>8000+ apps trust Plaid to quickly connect to financial institutions</Text>
          </View>
        </View>
        <View style={styles.featureContainer}>
          <ShieldIcon
            width={20}
            height={20}
            stroke={colors.darkFont}
            strokeWidth={1}
          />
          <View style={styles.featureTextContainer}>
            <Text style={styles.featureTitle}>Keep your data safe</Text>
            <Text style={styles.featureText}>Plaid uses best-in-class encryption to help protect your data</Text>
          </View>
        </View>
      </View>
      <View style={styles.divider} />
      <Text style={styles.disclaimer}>
        By continuing, you agree to Plaid's <Text style={styles.privacyLink}>Privacy Policy</Text> and to receiving updates on plaid.com
      </Text>
      <PrimaryButton
        title="Continue"
        onPress={() => {}}
      />
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
    alignItems: 'center'
  },
  logos: {
    width: 160,
    height: 50,
    marginBottom: 24,
  },
  features: {
    width: 320,
    height: 280,
    borderRadius: 16,
    paddingHorizontal: 20,
    paddingVertical: 18,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.borderLightGray,
    ...shadows.input,
    gap: 16,
    marginBottom: 24
  },
  featureContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
    width: 272
  },
  featureTextContainer: {
    width: 252
  },
  featureTitle: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.body,
    lineHeight: typography.lineHeight.medium
  },
  featureText: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.body,
    lineHeight: typography.lineHeight.medium
  },
  title: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.large,
    lineHeight: typography.lineHeight.xLarge,
    textAlign: 'center',
    marginBottom: 24
  },
  plaidText: {
    fontFamily: typography.fontFamily.bold,
    color: colors.black
  },
  noumiText: {
    fontFamily: typography.fontFamily.bold,
    color: colors.primaryGreen
  },
  divider: {
    marginVertical: 24,
    width: 600,
    height: 1,
    backgroundColor: colors.borderLightGray,
    alignSelf: 'center'
  },
  disclaimer: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.mini,
    color: colors.darkFont,
    textAlign: 'center',
    width: 312,
    marginBottom: 24
  },
  privacyLink: {
    textDecorationLine: 'underline'
  }
});
