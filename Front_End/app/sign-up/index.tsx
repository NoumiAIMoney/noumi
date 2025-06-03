import React, { useState } from 'react';
import {
  Keyboard,
  TouchableWithoutFeedback,
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import Checkbox from 'expo-checkbox';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';
import { colors, typography } from '@/src/theme';
import EyeIcon from '../../assets/icons/eye.svg';
import SmsIcon from '../../assets/icons/sms.svg';
import ProfileIcon from '../../assets/icons/profile.svg';
import { useRouter } from 'expo-router';

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
  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [agree, setAgree] = useState<boolean>(false);

  const router = useRouter();

  const isValid = name && email && password && agree;
  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <SafeAreaView style={styles.container}>
        <Text style={styles.logo}>Noumi</Text>

        <Text style={styles.heading}>Let’s get started</Text>
        <Text style={styles.sub}>
          Your journey to smarter finances begins now.
        </Text>

        <View style={styles.inputGroup}>
          <TextInput
            placeholder="Full Name"
            style={styles.input}
            placeholderTextColor={colors.lightGrayFont}
            value={name}
            onChangeText={setName}
          />
          <ProfileIcon
            width={20}
            height={20}
            fill="none"
            stroke={colors.lightGrayFont}
            strokeWidth={1.5}
          />
        </View>

        <View style={styles.inputGroup}>
          <TextInput
            placeholder="Email"
            style={styles.input}
            keyboardType="email-address"
            placeholderTextColor={colors.lightGrayFont}
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />
          <SmsIcon
            width={20}
            height={20}
            fill="none"
            stroke={colors.lightGrayFont}
            strokeWidth={1.5}
          />
        </View>

        <View style={styles.inputGroup}>
          <TextInput
            placeholder="Password"
            style={styles.input}
            secureTextEntry
            value={password}
            placeholderTextColor={colors.lightGrayFont}
            onChangeText={setPassword}
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
            color={agree ? '#6F1DF4' : undefined}
          />
          <Text style={styles.checkboxText}>
            By checking this box, I agree that I have read, understood, and consent to Noumi’s{' '}
            <Text style={styles.termsLink}>Terms of Use.</Text>
          </Text>
        </View>

        <TouchableOpacity
          style={[
            styles.primaryBtn,
            isValid ? styles.enabledBtn : styles.disabledBtn
          ]}
          disabled={!isValid}
          onPress={() => router.push('/onboarding/quiz')}
        >
          <Text style={styles.primaryText}>Get Started</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.loginContainer}
          onPress={() => router.push('/login')}
        >
          <Text style={styles.loginText}>
            Already have an account? <Text style={styles.loginLink}>Log In</Text>
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
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginVertical: 16,
    marginHorizontal: 10,
    borderRadius: 40,
    paddingHorizontal: 12,
    paddingBottom: 32
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
    color: '#593F90'
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
    alignSelf: 'center'
  },
  enabledBtn: {
    backgroundColor: '#593F90',
  },
  disabledBtn: {
    backgroundColor: colors.disabled,
  },
  primaryText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600'
  },
  loginContainer: {
    marginTop: 10,
    alignSelf: 'center'
  },
  loginText: {
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.body,
    color: colors.black,
  },
  loginLink: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.body,
    color: colors.black,
  },
});
