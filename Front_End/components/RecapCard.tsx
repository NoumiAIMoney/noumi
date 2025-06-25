import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { MaterialIcons } from '@expo/vector-icons';
import { colors, shadows, typography } from '@/src/theme';

interface RecapCardProps {
  dateRange: string;
  onPress: () => void;
}

const RecapCard: React.FC<RecapCardProps> = ({ dateRange, onPress }) => (
  <TouchableOpacity style={styles.card} onPress={onPress}>
    <View style={styles.left}>
      <View style={styles.icon}>
        <MaterialIcons name="emoji-events" size={24} color={colors.white} />
      </View>
      <View>
        <Text style={styles.date}>{dateRange}</Text>
        <Text style={styles.title}>Your Weekly Recap</Text>
      </View>
    </View>
    <Ionicons name="chevron-forward" size={20} color={colors.lightGrayFont} />
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
    ...shadows.input,
  },
  left: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primaryGreen,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  date: {
    fontSize: typography.fontSize.mini,
    color: colors.lightGrayFont,
  },
  title: {
    fontSize: typography.fontSize.body,
    fontFamily: typography.fontFamily.medium,
    color: colors.darkFont,
  },
});

export default RecapCard;
