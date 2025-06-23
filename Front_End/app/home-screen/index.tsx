import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Dimensions
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { MaterialIcons } from '@expo/vector-icons';
import Image1 from '@/assets/icons/fire.svg'; 
import Image2 from '@/assets/icons/money-send.svg'; 
import Image3 from '@/assets/icons/money-receive.svg';
import Image4 from '@/assets/icons/home.svg'; 
import Image5 from '@/assets/icons/goals.svg'; 
import Image6 from '@/assets/icons/progress.svg';
import Image7 from '@/assets/icons/empty-wallet-remove.svg';
import Image8 from '@/assets/icons/Fork-Knife.svg';

const { width } = Dimensions.get('window');

interface HomeScreenProps {
  navigation: any;
}

export default function HomeScreen({ navigation }: HomeScreenProps) {
  const userName: string = "Maya";
  
  return (
    <LinearGradient
      colors={['#2E6B70', '#F3F5F5']}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>M</Text>
            </View>
            <Text style={styles.greeting}>Good morning, {userName}</Text>
          </View>
          <TouchableOpacity style={styles.notificationBtn}>
            <Ionicons name="notifications-outline" size={24} color="#fff" />
          </TouchableOpacity>
        </View>

        {/* Trip Goal Card */}
        <View style={styles.goalCard}>
          <View style={styles.goalHeader}>
            <Text style={styles.goalTitle}>Trip to Mexico</Text>
            <Text style={styles.daysLeft}>129 days left</Text>
          </View>
          
          <View style={styles.goalAmount}>
            <Text style={styles.currentAmount}>$25</Text>
            <Text style={styles.totalAmount}> of $1200</Text>
          </View>
          
          <View style={styles.progressSection}>
            <Text style={styles.progressLabel}>Progress</Text>
            <Text style={styles.progressPercent}>7%</Text>
          </View>
          
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: '7%' }]} />
          </View>
          
          {/* Weekly Calendar */}
          <View style={styles.weeklyCalendar}>
            {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, index) => (
              <View key={index} style={styles.dayContainer}>
                <Text style={styles.dayLabel}>{day}</Text>
                <View style={styles.dayCircle}>
                  {index < 5 ? (
                    <Image1
                    />
                  ) : (
                    <View style={styles.emptyDay} />
                  )}
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Weekly Recap Card */}
        <TouchableOpacity 
          style={styles.recapCard}
          onPress={() => navigation.navigate('Progress')}
        >
          <View style={styles.recapContent}>
            <View style={styles.recapIcon}>
              <MaterialIcons name="emoji-events" size={24} color="#fff" />
            </View>
            <View style={styles.recapText}>
              <Text style={styles.recapDate}>05/26 - 05/31</Text>
              <Text style={styles.recapTitle}>Your Weekly Recap</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={22} color="#000000" marginLeft={-20}/>
        </TouchableOpacity>

        {/* My Spending Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>My Spending</Text>
            <TouchableOpacity>
              <Text style={styles.seeAllBtn}>See All</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.spendingRow}>
            <View style={styles.safeToSpendCard}>
              <Text style={styles.safeToSpendLabel}>Safe to Spend</Text>
              <Text style={styles.safeToSpendAmount}>$1,000.0</Text>
              <Text style={styles.updateDate}>Updated: 05/26/2025</Text>
            </View>
            
            <View style={styles.summaryCards}>
              <View style={styles.summaryCard}>
                <View style={[styles.summaryIcon, { backgroundColor: '#ffffff' }]}>
                  <Image3/>
                </View>
                <View>
                  <Text style={styles.summaryLabel}>Income</Text>
                  <Text style={styles.summaryAmount}>$ 6,000.0</Text>
                </View>
              </View>
              
              <View style={styles.summaryCard}>
                <View style={[styles.summaryIcon, { backgroundColor: '#ffffff' }]}>
                  <Image2/>
                </View>
                <View>
                  <Text style={styles.summaryLabel}>Expenses</Text>
                  <Text style={styles.summaryAmount}>$ 5,000.0</Text>
                </View>
              </View>
            </View>
          </View>
        </View>

        {/* My Habits Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>My Habits</Text>
            <TouchableOpacity>
              <Text style={styles.seeAllBtn}>See All</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.habitCard}>
            <View style={[styles.habitIcon, { backgroundColor: '#B4698F' }]}>
              <Image8 style={styles.habitIconImage} />
            </View>
            <Text style={styles.habitText}>
              Try meal planning instead of eating out at least twice.
            </Text>
          </View>
          
          <View style={styles.habitCard}>
            <View style={[styles.habitIcon, { backgroundColor: '#608762' }]}>
              <Image7 style={styles.habitIconImage} />
            </View>
            <Text style={styles.habitText}>
              Try a No-Spend-Day this week.
            </Text>
          </View>
        </View>
        </ScrollView>
        
        {/* Bottom Navigation */}
        <View style={styles.bottomNav}>
          <TouchableOpacity style={styles.navItem}>
            <Image4/>
            <Text style={styles.navTextActive}>Home</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.navItem}>
            <Image5/>
            <Text style={styles.navText}>Goals</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.navItem}>
            <Image6 />
            <Text style={styles.navText}>Progress</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontFamily: 'Inter',
    color: '#FFFFFF',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 30,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#D05F4E',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  greeting: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
  },
  notificationBtn: {
    padding: 8,
  },
  goalCard: {
    backgroundColor: '#fff',
    margin: 20,
    marginTop: 0,
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  goalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  goalTitle: {
    fontSize: 18,
    fontWeight: '600',
    fontFamily: 'Inter',
    color: '#191919',
  },
  daysLeft: {
    fontSize: 12,
    color: '#191919',
  },
  goalAmount: {
    flexDirection: 'row',
    alignItems: 'baseline',
    fontFamily: 'Inter',
    marginBottom: 12,
  },
  currentAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  totalAmount: {
    fontSize: 14,
    color: '#000000',
  },
  progressSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressLabel: {
    fontSize: 14,
    color: '#191919',
  },
  progressPercent: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 4,
    marginBottom: 20,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#D05F4E',
    borderRadius: 4,
  },
  weeklyCalendar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#EEF2F5',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    alignItems: 'center',
  },
  dayContainer: {
    alignItems: 'center',
    flex: 1,
    height: 30,
  },
  dayLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#191919',
    marginBottom: 8,
    height: 15,
    marginTop: -2,
  },
  dayCircle: {
    width: 20,
    height: 8,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  fireIcon: {
    width: 18,
    height: 18,
  },
  emptyDay: {
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#D1D5DB',
  },
  recapCard: {
    backgroundColor: '#fff',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  recapContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recapIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#377276',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  recapText: {
    flex: 1,
  },
  recapDate: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  recapTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#191919',
  },
  recapArrow: {
    marginLeft: 8,
    color: '#5E9B9C',
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 30,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#191919',
  },
  seeAllBtn: {
    fontSize: 14,
    color: '#5E9B9C',
    fontWeight: '500',
  },
  spendingRow: {
    flexDirection: 'row',
    gap: 12,
  },
  safeToSpendCard: {
    flex: 1,
    backgroundColor: '#D6E8E3',
    borderRadius: 12,
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  safeToSpendLabel: {
    fontSize: 14,
    color: '#191919',
    marginBottom: 8,
  },
  safeToSpendAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#191919',
    marginBottom: 8,
  },
  updateDate: {
    fontSize: 12,
    color: '#666',
  },
  summaryCards: {
    flex: 1,
    gap: 12,
  },
  summaryCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  summaryIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  summaryAmount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  habitCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  habitIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  habitIconImage: {
    // Add styles for the habit icon images if needed
  },
  habitText: {
    flex: 1,
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  bottomNav: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingTop: 20,
    paddingBottom: 10,
    paddingHorizontal: 20,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    bottom: 0,
  },
  navItem: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  navText: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  navTextActive: {
    fontSize: 12,
    color: '#000',
    marginTop: 4,
    fontWeight: '600',
  },
});