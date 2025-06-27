import { colors, shadows, typography } from '@/src/theme';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';

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
    height: 57,
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    elevation: 1,
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
