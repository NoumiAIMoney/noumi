import { useColorScheme as _useColorScheme, ColorSchemeName } from 'react-native';

export function useColorScheme(): ColorSchemeName {
  return _useColorScheme();
}
