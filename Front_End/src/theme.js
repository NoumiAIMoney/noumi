import { DarkTheme as NavigationDarkTheme, DefaultTheme as NavigationDefaultTheme } from '@react-navigation/native';

export const CustomLightTheme = {
  ...NavigationDefaultTheme,
  colors: {
    ...NavigationDefaultTheme.colors,
    background: '#F8F7FA',
    primary: '#4B0082',
  },
};

export const CustomDarkTheme = {
  ...NavigationDarkTheme,
  colors: {
    ...NavigationDarkTheme.colors,
    background: '#1E1E1E',
    primary: '#9B59B6',
  },
};

export const typography = {
  fontFamily: {
    fine: 'Inter_300Light',
    regular: 'Inter_400Regular',
    medium: 'Inter_500Medium',
    semiBold: 'Inter_600SemiBold',
    bold: 'Inter_700Bold',
    madimi: 'MadimiOne_400Regular',
  },
  fontSize: {
    mini: 12,
    small: 14,
    body: 16,
    large: 20,
    XLarge: 24,
    XXLarge: 32,
    XXXLarge: 36
  },
  lineHeight: {
    small: 18,
    body: 22,
    large: 26,
  },
  letterSpacing: {
    normal: 0,
  },
};

export const colors = {
  lightGrayFont: '#6D6D6D',
  darkFont: '#3A2960',
  primaryPurple: '#503984',
  lightPurple: '#DED8EC',
  disabled: '#9EA1A8',
  white: '#FFFFFF',
  black: '#000000',
  gray: '#555555',
  lightGray: '#F8F7FA',
  logo: '#593F90',
  lightGrayBackground: "#F5F5F8",
  muted: '#888888',
};

export const shadows = {
  input: {
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 1,
  },
};
