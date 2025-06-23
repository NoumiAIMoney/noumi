import SpikeBar from '@/components/SpikeBar';
import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import HorizontalCard from '@/components/HorizontalCard';
import TrendUpIcon from '@/assets/icons/progress.svg'
import { getYearlyAnomalies } from '@/src/api/anomalies';
import { getSpendingCategories } from '@/src/api/spending';
import { getSpendingTrends } from '@/src/api/trends';
import CategoryVerticalCard from '@/components/CategoryVerticalCard';

export default function Step1() {
  const [anomalies, setAnomalies] = useState<number[] | null>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [anomaliesRes, trendsRes, categoriesRes] = await Promise.all([
          getYearlyAnomalies(),
          getSpendingTrends(),
          getSpendingCategories()
        ]);

        setAnomalies(anomaliesRes.anomalies);
        setTrends(trendsRes || []);
        setCategories(categoriesRes || []);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  if (!anomalies) return null;

  return (
    <View style={styles.container}>
      <View style={styles.textGroup}>
        <Text style={styles.titleSpending}>Spending Analysis</Text>
      </View>
      <View style={styles.cardWrapper}>
        <View style={styles.avatar}><Text style={styles.initial}>M</Text></View>
        <View style={styles.card}>
          <Text style={styles.mainTitle}>Your past 12 months</Text>
          <Text style={styles.subtitle}>Impulse spending spikes</Text>
          <SpikeBar progress={anomalies} />

          <Text style={styles.subtitle}>Spending trends</Text>
          {trends.slice(0, 2).map((trend, index) => (
            <HorizontalCard
              key={index}
              title={trend.trend || 'N/A'}
              white={false}
              icon={<TrendUpIcon width={24} height={24} fill="none" />}
              width={330}
            />
          ))}
          <Text style={styles.subtitle}>Top 3 spending categories</Text>
          <View style={styles.horizontalCardContainer}>
            {categories.slice(0, 3).map((category, index) => (
              <CategoryVerticalCard
                key={index}
                icon={<TrendUpIcon width={24} height={24} fill="none" />}
                label={category.category_name}
              />
            ))}
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.greenBackground,
    paddingHorizontal: 20,
    paddingTop: 64
  },
  textGroup: {
    alignItems: 'flex-end'
  },
  titleSpending: {
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.lighterFont,
    lineHeight: typography.lineHeight.XXLarge
  },
  cardWrapper: {
    position: 'relative',
    marginTop: 8,
    alignSelf: 'flex-start',
    marginLeft: 0,
  },
  avatar: {
    position: 'absolute',
    top: -25,
    left: 18,
    width: 50,
    height: 50,
    borderRadius: 50,
    backgroundColor: colors.progressBarOrange,
    paddingVertical: 12,
    paddingHorizontal: 14,
    zIndex: 2,
  },
  initial: {
    color: colors.white,
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XLarge
  },
  card: {
    width: 363,
    height: 623,
    borderRadius: 16,
    backgroundColor: colors.white,
    paddingTop: 40,
    paddingRight: 16,
    paddingBottom: 40,
    paddingLeft: 16,
    shadowColor: '#191919',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 8,
    zIndex: 1,
  },
  mainTitle: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XLarge,
    color: colors.darkFont,
    marginBottom: 8
  },
  subtitle: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.large,
    lineHeight: typography.lineHeight.body,
    color: colors.darkFont,
    marginTop: 16,
    marginBottom: 8
  },
  amount: {
    fontFamily: typography.fontFamily.bold,
    fontSize: typography.fontSize.XXXXLarge,
    lineHeight: typography.lineHeight.XXLarge,
    color: colors.black
  },
  horizontalCardContainer: {
    flexDirection: 'row',
    gap: 24,
    marginTop: 8,
  }
});
