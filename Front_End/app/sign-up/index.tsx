import { colors, typography } from '@/src/theme';
import Checkbox from 'expo-checkbox';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import {
  Keyboard,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  TouchableWithoutFeedback,
  View,
} from 'react-native';
import EyeIcon from '../../assets/icons/eye.svg';
import ProfileIcon from '../../assets/icons/profile.svg';
import SmsIcon from '../../assets/icons/sms.svg';

export default function SignUpScreen() {
  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [nameFocused, setNameFocused] = useState(false);
  const [emailFocused, setEmailFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [agree, setAgree] = useState<boolean>(false);

  const router = useRouter();

  const isValid = name && email && password;
  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <SafeAreaView style={styles.container}>
        <Text style={styles.logo}>Noumi</Text>

        <Text style={styles.heading}>Let's get started</Text>
        <Text style={styles.sub}>
          Your journey to smarter finances begins now.
        </Text>
        <View style={[styles.inputGroup, nameFocused && styles.inputFocused]}>
          <TextInput
            placeholder="Full Name"
            style={styles.input}
            placeholderTextColor={colors.lightGrayFont}
            autoCapitalize="none"
            value={name}
            onChangeText={setName}
            onFocus={() => setNameFocused(true)}
            onBlur={() => setNameFocused(false)}
          />
          <ProfileIcon
            width={20}
            height={20}
            fill="none"
            stroke={colors.lightGrayFont}
            strokeWidth={1.5}
          />
        </View>

        <View style={[styles.inputGroup, emailFocused && styles.inputFocused]}>
          <TextInput
            placeholder="Email"
            style={styles.input}
            keyboardType="email-address"
            placeholderTextColor={colors.lightGrayFont}
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
            onFocus={() => setEmailFocused(true)}
            onBlur={() => setEmailFocused(false)}
          />
          <SmsIcon
            width={20}
            height={20}
            fill="none"
            stroke={colors.lightGrayFont}
            strokeWidth={1.5}
          />
        </View>

        <View style={[styles.inputGroup, passwordFocused && styles.inputFocused]}>
          <TextInput
            placeholder="Password"
            style={styles.input}
            secureTextEntry
            value={password}
            placeholderTextColor={colors.lightGrayFont}
            onChangeText={setPassword}
            onFocus={() => setPasswordFocused(true)}
            onBlur={() => setPasswordFocused(false)}
          />
          <EyeIcon
            width={20}
            height={20}
            fill="none"
            stroke={colors.lightGrayFont}
            strokeWidth={1.5}
          />
        </View>
        <View style={styles.checkboxRow}>
          <Checkbox
            value={agree}
            onValueChange={setAgree}
            style={styles.customCheckbox}
            color={agree ? colors.primaryGreen : undefined}
          />
          <Text style={styles.checkboxText}>
            By checking this box, I agree that I have read, understood, and consent to Noumi’s{' '}
            <Text style={styles.termsLink}>Terms of Use.</Text>
          </Text>
        </View>

        <TouchableOpacity
          style={[
            styles.primaryBtn,
            isValid ? styles.enabledBtn : styles.disabledBtn,
          ]}
          disabled={!isValid}
          onPress={()=> router.replace('/onboarding/quiz')}
        >
          <Text style={styles.primaryText}>Get Started</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.signUpContainer}
          onPress={() => router.push('/login')}
        >
          <Text style={styles.signUpText}>
            Already have an account? <Text style={styles.signUpLink}>Log In</Text>
          </Text>
        </TouchableOpacity>
      </SafeAreaView>
    </TouchableWithoutFeedback>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  logo: {
    fontFamily: typography.fontFamily.madimi,
    fontSize: typography.fontSize.XXXLarge,
    color: colors.primaryGreen,
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
    marginBottom: 64,
    textAlign: 'left',
    width: '100%',
    maxWidth: 370,
    paddingHorizontal: 10,
  },
  inputGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 16,
    marginBottom: 12,
    marginHorizontal: 20,
    elevation: 2,
    height: 56
  },
  input: {
    flex: 1,
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.regular,
    color: colors.black,
    marginRight: 12
  },
  inputFocused: {
    borderColor: colors.primaryGreen,
    borderWidth: 1,
    shadowColor: '#00014',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 4,
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginVertical: 16,
    marginHorizontal: 10,
    borderRadius: 40,
    paddingHorizontal: 12,
  },
  customCheckbox: {
    width: 16,
    height: 16,
    borderRadius: 4,
    padding: 3,
    borderWidth: 2,
    borderColor: '#8E8E93',
    marginTop: 6
  },
  checkboxText: {
    flex: 1,
    marginLeft: 8,
    marginRight: 24,
    fontFamily: typography.fontFamily.fine,
    fontSize: typography.fontSize.mini,
    color: colors.black,
  },
  termsLink: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.mini,
    color: colors.primaryGreen
  },
  primaryBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '80%',
    maxWidth: 312,
    height: 56,
    borderRadius: 25,
    marginVertical: 8,
    alignSelf: 'center',
    marginTop: 60
  },
  enabledBtn: {
    backgroundColor: colors.primaryGreen,
  },
  disabledBtn: {
    backgroundColor: colors.disabled,
  },
  primaryText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600'
  },
  signUpContainer: {
    marginTop: 10,
    alignSelf: 'center'
  },
  signUpText: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.body,
    color: colors.black,
  },
  signUpLink: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.body,
    color: colors.primaryGreen,
  },
});
