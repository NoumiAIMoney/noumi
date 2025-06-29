import { categoryIcons } from '@/components/CategoryIcons';
import HorizontalCard from '@/components/HorizontalCard';
import { getSpendingCategories } from '@/src/api/spending';
import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

type SpendingCategory = {
  category: string;
  decreaseAmount: number;
  percentageDrop: number;
  previousAmount: number;
} | null;

function getCategoryWithHighestDecrease(data: { category_name: string; amount: number; month: string; }[]) {
  const grouped: Record<string, { [month: string]: number }> = {};

  // Group data by category and month
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

    const [secondLastMonth, secondLastAmount] = monthEntries[monthEntries.length - 2];
    const [lastMonth, lastAmount] = monthEntries[monthEntries.length - 1];

    const drop = secondLastAmount - lastAmount;

    if (drop > maxDrop) {
      maxDrop = drop;
      const percentageDrop = (drop / secondLastAmount) * 100;
      result = {
        category,
        // TO DO: NEED TO CHANGE VAR NAMES
        decreaseAmount: parseFloat(lastAmount.toFixed(2)) / 4,
        percentageDrop: parseFloat(percentageDrop.toFixed(2)),
        previousAmount: parseFloat(secondLastAmount.toFixed(2)) / 4,
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
        console.log(data)
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  if (!category) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Great job! You decreased your {category.category} spending by {Math.round(category.percentageDrop)}%.</Text>
      <Text style={styles.subtitle}>This week</Text>
      <View style={styles.cardsWrapper}>
        <HorizontalCard
          title={category.category || 'N/A'}
          white={true}
          icon={
            <View style={styles.iconWrapper}>
              {categoryIcons[category.category || 'Uncategorized'] || categoryIcons['Uncategorized']}
            </View>
          }
          amount={`${category.decreaseAmount.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`}
          // amountColor='#1BB16A'
          onlyLabel
          withShadow
        />
      </View>
      <Text style={styles.subtitle}>Last week</Text>
      <View style={styles.cardsWrapper}>
        <HorizontalCard
          title={category.category || 'N/A'}
          white={true}
          icon={
            <View style={styles.iconWrapper}>
              {categoryIcons[category.category || 'Uncategorized'] || categoryIcons['Uncategorized']}
            </View>
          }
          amount={
            category.previousAmount.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })
          }
          onlyLabel
          withShadow
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
    marginBottom: 48,
    marginLeft: 8,
    marginRight: 10,
    width: 300
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
  },
  cardsWrapper: {
    alignItems: 'center',
  },
});

