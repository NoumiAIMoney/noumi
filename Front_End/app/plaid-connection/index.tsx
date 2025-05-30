import React from 'react';
import { View, StyleSheet } from 'react-native';

export default function QuizScreen() {
  return (
    <View style={styles.container}>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingVertical: 24,
    paddingHorizontal: 12,
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  button: {
    marginTop: 16,
  },
});
