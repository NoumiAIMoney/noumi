import { colors, typography } from '@/src/theme';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export default function Step1() {
  return (
    <View style={styles.container}>
      <View style={styles.textGroup}>
        <Text style={styles.titleWeekly}>Spending Analysis</Text>
      </View>
      <View style={styles.cardWrapper}>
        <View style={styles.avatar}><Text style={styles.initial}>M</Text></ View>
        <View style={styles.card}>
          <Text style={styles.mainTitle}>You are on a roll, Maya!</Text>
          <Text style={styles.subtitle}>This week's savings</Text>
          <Text style={styles.amount}>$100</Text>
          <Text style={styles.subtitle}>Goal progress</Text>
          <Text style={styles.subtitle}>7%</Text>
          {/* PROGRESS BAR */}
          <Text style={styles.subtitle}>Your Weekly Stats</Text>
          {/* CARDS */}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.greenBackground,
    paddingHorizontal: 20,
    paddingTop: 64
  },
  textGroup: {
    alignItems: 'flex-end'
  },
  titleWeekly: {
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.lighterFont,
    lineHeight: typography.lineHeight.XXLarge
  },
  cardWrapper: {
    position: 'relative',
    marginTop: 8,
    alignSelf: 'flex-start',
    marginLeft: 0,
  },
  avatar: {
    position: 'absolute',
    top: -25,
    left: 18,
    width: 50,
    height: 50,
    borderRadius: 50,
    backgroundColor: colors.progressBarOrange,
    paddingVertical: 12,
    paddingHorizontal: 14,
    zIndex: 2,
  },
  initial: {
    color: colors.white,
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XLarge
  },
  card: {
    width: 353,
    height: 543,
    borderRadius: 16,
    backgroundColor: colors.white,
    paddingTop: 40,
    paddingRight: 16,
    paddingBottom: 40,
    paddingLeft: 16,
    shadowColor: '#191919',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 8,
    zIndex: 1,
  },
  mainTitle: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XLarge,
    color: colors.darkFont
  },
  subtitle: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.large,
    lineHeight: typography.lineHeight.body,
    color: colors.darkFont
  },
  amount: {
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.XXXXLarge,
    lineHeight: typography.lineHeight.XXLarge,
    color: colors.black
  }
});
