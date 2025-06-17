import { colors, typography } from '@/src/theme';
import { RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
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
import SmsIcon from '../../assets/icons/sms.svg';

type RootStackParamList = {
  SignUp: undefined;
  Login: undefined;
};

type SignUpScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'SignUp'
>;

type SignUpScreenProps = {
  navigation: SignUpScreenNavigationProp;
  route: RouteProp<RootStackParamList, 'SignUp'>;
};

export default function SignUpScreen({ navigation }: SignUpScreenProps) {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [emailFocused, setEmailFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);

  const router = useRouter();

  const isValid = email && password;
  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <SafeAreaView style={styles.container}>
        <Text style={styles.logo}>Noumi</Text>

        <Text style={styles.heading}>Welcome back</Text>
        <Text style={styles.sub}>
          Your journey to smarter finances begins now.
        </Text>
        <View style={[styles.inputGroup, emailFocused && styles.inputFocused]}>
          {/* TO DO: ADD INPUT ON FOCUS */}
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

        <TouchableOpacity
          // TODO: UPDATE
          onPress={() => {}}
          style={{ alignSelf: 'flex-start' }}
        >
          <Text style={styles.forgotPassword}>Forgot Password?</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.primaryBtn,
            isValid ? styles.enabledBtn : styles.disabledBtn,
          ]}
          disabled={!isValid}
        >
          <Text style={styles.primaryText}>Log In</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.signUpContainer}
          onPress={() => router.push('/sign-up')}
        >
          <Text style={styles.signUpText}>
            New to Noumi? <Text style={styles.signUpLink}>Create Account</Text>
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
    shadowColor: '#00014',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 4,
  },
  forgotPassword: {
    fontFamily: typography.fontFamily.medium,
    fontSize: typography.fontSize.small,
    paddingLeft: 20,
    color: colors.primaryGreen,
    paddingTop: 10,
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
    marginTop: 120
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
