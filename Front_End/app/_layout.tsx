import React from 'react';
import { ThemeProvider } from '@react-navigation/native';
import { useFonts, 
  Inter_400Regular, 
  Inter_500Medium, 
  Inter_600SemiBold, 
  Inter_700Bold 
} from '@expo-google-fonts/inter';
import { useFonts as useMadimiOne, MadimiOne_400Regular } from '@expo-google-fonts/madimi-one';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';

import { CustomLightTheme, CustomDarkTheme } from '../src/theme';

export default function RootLayout() {

  const [mainFontsLoaded] = useFonts({
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
      <Stack screenOptions={{ headerShown: false }} />
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}
