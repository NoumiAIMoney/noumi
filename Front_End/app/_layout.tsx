import {
  Inter_300Light,
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
  useFonts
} from '@expo-google-fonts/inter';
import { MadimiOne_400Regular, useFonts as useMadimiOne } from '@expo-google-fonts/madimi-one';
import { ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import 'react-native-reanimated';

import { CustomLightTheme } from '../src/theme';

export default function RootLayout() {

  const [mainFontsLoaded] = useFonts({
    Inter_300Light,
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
  });

  const [fontsMadimiLoaded] = useMadimiOne({ MadimiOne_400Regular });
  if (!mainFontsLoaded && !fontsMadimiLoaded) {
    return null;
  }

  // WHEN DARK MODE NEEDS TO BE IMPLEMENTED
  // const theme = colorScheme === 'dark' ? CustomDarkTheme : CustomLightTheme;
  const theme = CustomLightTheme;

  return (
    <ThemeProvider value={theme}>
      <Stack screenOptions={{ headerShown: false, gestureEnabled: true }}  />
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}
