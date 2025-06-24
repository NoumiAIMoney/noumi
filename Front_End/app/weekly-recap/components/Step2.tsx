import HorizontalCard from '@/components/HorizontalCard';
import { getSpendingCategories } from '@/src/api/spending';
import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import CarIcon from '@/assets/icons/car.svg'

type SpendingCategory = {
  category: string;
  decreaseAmount: number;
  percentageDrop: number;
  previousAmount: number;
} | null;

function getCategoryWithHighestDecrease(data: { category_name: string; amount: number; month: string; }[]) {
  const grouped: Record<string, { [month: string]: number }> = {};

  data.forEach(({ category_name, amount, month }) => {
    if (!grouped[category_name]) grouped[category_name] = {};
    grouped[category_name][month] = amount;
  });

  let maxDrop = -Infinity;
  let result: {
    category: string;
    decreaseAmount: number;
    percentageDrop: number;
    previousAmount: number;
  } | null = null;

  for (const [category, months] of Object.entries(grouped)) {
    const monthEntries = Object.entries(months).sort(([a], [b]) => a.localeCompare(b));
    if (monthEntries.length < 2) continue;

    const [prevMonth, prevAmount] = monthEntries[0];
    const [currMonth, currAmount] = monthEntries[1];

    const drop = prevAmount - currAmount;

    if (drop > maxDrop) {
      maxDrop = drop;
      const percentageDrop = (drop / prevAmount) * 100;
      result = {
        category,
        decreaseAmount: parseFloat(drop.toFixed(2)),
        percentageDrop: parseFloat(percentageDrop.toFixed(2)),
        previousAmount: prevAmount,
      };
    }
  }

  return result;
}

export default function Step2() {
  const [category, setCategory] = useState<SpendingCategory>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getSpendingCategories();
        setCategory(getCategoryWithHighestDecrease(data));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  if (!category) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Great job! You decreased your Coffee Shops spending by 28%.</Text>
      <Text style={styles.subtitle}>This week</Text>
      <View style={styles.cardsWrapper}>
        <HorizontalCard
          title={category.category || 'N/A'}
          white={true}
          icon={
            <View style={styles.iconWrapper}>
              <CarIcon width={24} height={24} fill="none" stroke={colors.white} />
            </View>
          }
          amount={`-${String(category.decreaseAmount)}`}
          amountColor='#1BB16A'
          onlyLabel
        />
      </View>
      <Text style={styles.subtitle}>Last week</Text>
      <View style={styles.cardsWrapper}>
        <HorizontalCard
          title={category.category || 'N/A'}
          white={true}
          icon={
            <View style={styles.iconWrapper}>
              <CarIcon width={24} height={24} fill="none" stroke={colors.white} />
            </View>
          }
          amount={String(category.previousAmount)}
          onlyLabel
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.greenBackground,
    paddingHorizontal: 20,
    paddingTop: 64,
  },
  text: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.darkFont,
    letterSpacing: 0,
    marginBottom: 16,
    marginLeft: 8,
    marginRight: 24
  },
  subtitle: {
    fontFamily: typography.fontFamily.medium,
    color: colors.darkFont,
    fontSize: typography.fontSize.body,
    marginVertical: 12,
    marginLeft: 8
  },
  iconWrapper: {
    width: 39.09,
    height: 40,
    padding: 10,
    borderRadius: 100,
    backgroundColor: '#9C5538',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8
  },
  cardsWrapper: {
    alignItems: 'center',
  },
});

