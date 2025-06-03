import React from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import GoogleIcon from '../../assets/icons/google.svg';
import { AntDesign } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { colors, typography } from '@/src/theme';

export default function AuthSelectionScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.logo}>Noumi</Text>
      <Text style={styles.heading}>Let’s get started</Text>
      <Text style={styles.sub}>
        Your journey to smarter finances begins now.
      </Text>

      <TouchableOpacity
        style={[styles.btn, styles.primaryBtn]}
        onPress={() => router.push('/sign-up')}
      >
        <Text style={[styles.btnText, styles.primaryText]}>
          Sign Up with Email
        </Text>
      </TouchableOpacity>

      <Text style={styles.or}>or</Text>

      <TouchableOpacity
        style={[styles.btn, styles.secondaryBtn]}
        onPress={() => {
          // TODO: Handle Apple auth
        }}
      >
        <AntDesign name="apple1" size={20} style={styles.icon} />
        <Text style={styles.btnText}>Continue with Apple</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.btn, styles.secondaryBtn]}
        onPress={() => {
          // TODO: Handle Google auth
        }}
      >
        <GoogleIcon
          width={20}
          height={20}
          style={styles.icon}
        />
        <Text style={styles.btnText}>Continue with Google</Text>
      </TouchableOpacity>

      <View style={styles.footer}>
        <Text style={styles.footerText}>Already have an account? </Text>
        <TouchableOpacity onPress={() => router.push('/login')}>
          <Text style={[styles.footerText, styles.loginText]}>Log In</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.white,
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  logo: {
    fontFamily: typography.fontFamily.madimi,
    fontSize: typography.fontSize.XXXLarge,
    color: colors.primaryPurple,
    marginTop: 50,
  },
  heading: {
    fontSize: typography.fontSize.XLarge,
    fontFamily: typography.fontFamily.semiBold,
    marginTop: 40,
    textAlign: 'left',
    color: colors.black,
    width: '100%',
    maxWidth: 350,
    marginBottom: 10,
  },
  sub: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.body,
    color: colors.black,
    marginBottom: 40,
    textAlign: 'left',
    width: '100%',
    maxWidth: 370,
    paddingHorizontal: 10,
  },
  btn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '80%',
    maxWidth: 350,
    height: 50,
    borderRadius: 25,
    borderWidth: 1,
    borderColor: colors.black,
    marginVertical: 8,
    alignSelf: 'center',
  },
  primaryBtn: {
    backgroundColor: colors.primaryPurple,
    borderWidth: 0,
  },
  secondaryBtn: {
    backgroundColor: colors.white,
  },
  btnText: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.body
  },
  primaryText: {
    color: '#fff',
  },
  icon: {
    marginRight: 8,
    color: '#333',
  },
  or: {
    marginVertical: 15,
    fontSize: typography.fontSize.body,
    color: colors.black,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 20,
  },
  footerText: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.body,
    color: colors.black,
  },
  loginText: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.body,
    color: colors.black,
  },
});
