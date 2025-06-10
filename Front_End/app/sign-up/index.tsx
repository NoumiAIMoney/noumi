import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  TextStyle,
  ViewStyle,
  NativeSyntheticEvent,
  TextInputChangeEventData,
} from 'react-native';
import Checkbox from 'expo-checkbox';
import { Ionicons } from '@expo/vector-icons';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

// Define navigation prop type
type RootStackParamList = {
  Login: undefined;
  SignUp: undefined;
};

type SignUpScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'SignUp'>;
};

const SignUpScreen: React.FC<SignUpScreenProps> = ({ navigation }) => {
  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [agree, setAgree] = useState<boolean>(false);
  const [showPassword, setShowPassword] = useState<boolean>(false);

  const isValid = name.length > 0 && email.length > 0 && password.length > 0 && agree;

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.logo}>Noumi</Text>

      <Text style={styles.heading}>Let's get started</Text>
      <Text style={styles.sub}>
        Your journey to smarter finances begins now.
      </Text>

      {/* Full Name Input */}
      <View style={styles.inputGroup}>
        <TextInput
          placeholder="Full Name"
          style={styles.input}
          value={name}
          onChangeText={setName}
          placeholderTextColor="#888"
        />
        <Ionicons name="person-outline" size={20} color="#888" />
      </View>

      {/* Email Input */}
      <View style={styles.inputGroup}>
        <TextInput
          placeholder="Email"
          style={styles.input}
          keyboardType="email-address"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
          placeholderTextColor="#888"
        />
        <Ionicons name="mail-outline" size={20} color="#888" />
      </View>

      {/* Password Input */}
      <View style={styles.inputGroup}>
        <TextInput
          placeholder="Password"
          style={styles.input}
          secureTextEntry={!showPassword}
          value={password}
          onChangeText={setPassword}
          placeholderTextColor="#888"
        />
        <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
          <Ionicons
            name={showPassword ? 'eye-off-outline' : 'eye-outline'}
            size={20}
            color="#888"
          />
        </TouchableOpacity>
      </View>

      {/* Checkbox */}
      <View style={styles.checkboxRow}>
        <Checkbox
          value={agree}
          onValueChange={setAgree}
          style={styles.checkbox}
          color={agree ? '#503984' : undefined}
        />
        <Text style={styles.checkboxText}>
          By checking this box, I agree that I have read, understood, and consent
          to Noumi’s <Text style={styles.termsLink}>Terms of Use.</Text>
        </Text>
      </View>

      <TouchableOpacity
        style={[
          styles.primaryBtn,
          isValid ? styles.enabledBtn : styles.disabledBtn
        ]}
        disabled={!isValid}
      >
        <Text style={styles.primaryText}>Get Started</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.loginContainer}
        onPress={() => navigation.navigate('Login')}
      >
        <Text style={styles.loginText}>
          Already have an account? <Text style={styles.loginLink}>Log In</Text>
        </Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

export default SignUpScreen;

type Styles = {
  [key: string]: ViewStyle | TextStyle;
};

const styles = StyleSheet.create<Styles>({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#F5F5F8'
  },
  logo: {
    fontFamily: 'MadimiOne',
    fontSize: 36,
    color: '#503984',
    marginTop: 60,
    marginBottom: 20,
    textAlign: 'center',
    width: 102,
    height: 48,
    alignSelf: 'center',
  },
  heading: {
    fontSize: 24,
    fontWeight: '600',
    fontFamily: 'Inter',
    height: 22,
    marginTop: 22,
    width: 353,
    lineHeight: 22,
    letterSpacing: 0,
    marginLeft: 20,
    marginBottom: 16,
    color: '#191919'
  },
  sub: {
    fontSize: 16,
    color: '#191919',
    fontFamily: 'Inter',
    height: 22,
    marginLeft: 20,
    marginBottom: 50,
    width: 353,
    lineHeight: 22,
    letterSpacing: 0
  },
  inputGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    height: 56,
    gap: 16,
    borderRadius: 16,
    marginLeft: 20,
    marginRight: 20,
    paddingHorizontal: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 2
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#424242',
    marginRight: 12
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
    marginLeft: 20,
    marginRight: 20,
    gap: 10,
  },
  checkbox: {
    width: 16,
    height: 16,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: '#8E8E93',
    padding: 3,
  },
  checkboxText: {
    flex: 1,
    fontSize: 12,
    color: '#000000',
    fontFamily: 'Inter',
    fontWeight: '300',
    lineHeight: 15,
  },
  termsLink: {
    color: '#503984',
    fontWeight: '600'
  },
  primaryBtn: {
    alignItems: 'center',
    justifyContent: 'center',
    height: 56,
    borderRadius: 25,
    marginTop: 60,
    marginVertical: 8,
    marginBottom: 0,
    alignSelf: 'center',
    width: '80%',
    maxWidth: 312,
    borderWidth: 1,
  },
  enabledBtn: {
    backgroundColor: '#593F90',
    borderColor: '#593F90'
  },
  disabledBtn: {
    backgroundColor: '#999',
    borderColor: '#ccc'
  },
  primaryText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  loginContainer: {
    marginTop: 20,
    alignSelf: 'center'
  },
  loginText: {
    fontSize: 16,
    color: '#24201E'
  },
  loginLink: {
    color: '#24201E',
    fontWeight: '600'
  }
});
