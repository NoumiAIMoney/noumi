import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { getYearlyAnomalies } from '@/src/api/anomalies';
import { getSpendingTrends } from '@/src/api/trends';
import HorizontalCard from '@/components/HorizontalCard';
import TrendUpIcon from '@/assets/icons/progress.svg'

export default function Step3() {
  const [anomalies, setAnomalies] = useState<number[] | null>(null);
  const [trends, setTrends] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [anomaliesRes, trendsRes] = await Promise.all([
          getYearlyAnomalies(),
          getSpendingTrends(),
        ]);

        setAnomalies(anomaliesRes.anomalies);
        setTrends(trendsRes || []);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  if (!anomalies) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.subtitle}>Habits</Text>
      <View style={styles.section}>
        {trends.slice(0, 2).map((trend, index) => (
          <HorizontalCard
            key={index}
            title={trend.trend || 'N/A'}
            white={true}
            icon={<TrendUpIcon width={24} height={24} fill="none" />}
            width={330}
          />
        ))}
      </View>
      <Text style={styles.text}>Way to go! You're building new habits and they are paying off.</Text>
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
  text: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.darkFont,
    letterSpacing: 0,
    marginLeft: 16,
    marginBottom: 24
  },
  section: {
    alignItems: 'center',
    marginBottom: 32
  },
  subtitle: {
    fontFamily: typography.fontFamily.medium,
    color: colors.darkFont,
    fontSize: typography.fontSize.body,
    marginVertical: 12,
    marginLeft: 16,
  },
});
