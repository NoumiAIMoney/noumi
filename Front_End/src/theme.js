import { DarkTheme as NavigationDarkTheme, DefaultTheme as NavigationDefaultTheme } from '@react-navigation/native';

export const CustomLightTheme = {
  ...NavigationDefaultTheme,
  colors: {
    ...NavigationDefaultTheme.colors,
    background: '#F3F5F5',
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
    XXLarge: 30,
    XXXLarge: 36,
    XXXXLarge: 40
  },
  lineHeight: {
    small: 18,
    medium: 20,
    body: 22,
    large: 26,
    xLarge: 28,
    XXLarge: 40
  },
  letterSpacing: {
    normal: 0,
  },
};

export const colors = {
  lightGrayFont: '#6D6D6D',
  darkFont: '#191919',
  primaryGreen: '#316E72',
  lightPurple: '#DED8EC',
  disabled: '#9EA1A8',
  white: '#FFFFFF',
  black: '#000000',
  gray: '#555555',
  lightGray: '#F8F7FA',
  borderLightGray: '#E7E8E7',
  progressBarOrange: '#D05F4E',
  progressBarOrangeLight: '#EDDEDD',
  lightBackground: '#F3F5F5',
  greenBackground: '#D6E8E3',
  muted: '#888888',
  lighterFont: 'rgba(25, 25, 25, 0.698)',
  grayFont: '#939393',
  lightGrayBackground: '#F0F0F0',
  blueFont: '#377CC8'
};

export const shadows = {
  input: {
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
};
