import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { getYearlyAnomalies } from '@/src/api/anomalies';
import SpikeBar from '@/components/SpikeBar';
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
      <Text style={styles.text}>Impulse spending spikes in the past 12 months.</Text>
      <View style={styles.section}>
        <SpikeBar progress={anomalies} />
      </View>
      <View style={styles.section}>
        {trends.slice(0, 4).map((trend, index) => (
          <HorizontalCard
            key={index}
            title={trend.trend || 'N/A'}
            white={true}
            icon={<TrendUpIcon width={24} height={24} fill="none" />}
            width={330}
          />
        ))}
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
  text: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.darkFont,
    letterSpacing: 0,
    marginLeft: 8,
    marginBottom: 24
  },
  section: {
    alignItems: 'center',
    marginBottom: 32
  }
});
