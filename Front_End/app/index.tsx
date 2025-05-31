import React from 'react';
import { StyleSheet, Text, View, Pressable, GestureResponderEvent } from 'react-native';
import { useRouter } from 'expo-router';
import { useTheme } from '@react-navigation/native';

export default function Page() {
  const router = useRouter();
  const { colors } = useTheme();

  const handlePress = (event: GestureResponderEvent) => {
    router.push('/onboarding');
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={styles.main}>
        <Text style={[styles.title, { color: colors.text }]}>Hello World</Text>
        <Text style={[styles.subtitle, { color: colors.text }]}>This is the first page of your app.</Text>
        <Pressable style={styles.button} onPress={handlePress}>
          <Text style={styles.buttonText}>Start Onboarding</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    padding: 24,
  },
  main: {
    flex: 1,
    justifyContent: 'center',
    maxWidth: 960,
    marginHorizontal: 'auto',
  },
  title: {
    fontSize: 64,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 36,
    color: '#38434D',
  },
  button: {
    borderRadius: 25,
    backgroundColor: '#4B0082',
    paddingVertical: 14,
    paddingHorizontal: 40,
    alignSelf: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
  },
});
