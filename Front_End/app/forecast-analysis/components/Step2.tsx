import { categoryIcons } from '@/components/CategoryIcons';
import HorizontalCard from '@/components/HorizontalCard';
import { getSpendingCategories } from '@/src/api/spending';
import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

type SpendingCategory = {
  category_name: string;
  amount: number;
  month: string;
};

const COLORS = ['#B4698F', '#E97272', '#FFCE51']

function getTop3CategoriesForLatestMonth(data: SpendingCategory[]): SpendingCategory[] {
  const months = [...new Set(data.map(item => item.month))];
  const latestMonth = months.sort().pop();

  if (!latestMonth) return [];

  const filtered = data.filter(item => item.month === latestMonth);
  console.log(filtered)

  return filtered
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 3);
}

export default function Step2() {
  const [categories, setCategories] = useState<SpendingCategory[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getSpendingCategories();

        setCategories(getTop3CategoriesForLatestMonth(data));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);
  if (!categories) return null;
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Be aware of your top three spending categories.</Text>
      <Text style={styles.subtitle}>Monthly Average</Text>
      <View style={styles.cardsWrapper}>
        {categories.slice(0, 3).map((category, index) => (
          <HorizontalCard
            key={index}
            title={category.category_name || 'N/A'}
            white={true}
            icon={
              <View style={[styles.iconWrapper, {backgroundColor: COLORS[index]}]}>
                {categoryIcons[category.category_name || 'Uncategorized'] || categoryIcons['Uncategorized']}
              </View>
            }
            amount={category.amount.toString()}
            onlyLabel
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
    paddingTop: 64,
  },
  text: {
    fontFamily: typography.fontFamily.semiBold,
    fontSize: typography.fontSize.XXLarge,
    color: colors.darkFont,
    letterSpacing: 0,
    marginBottom: 16,
    marginLeft: 8
  },
  subtitle: {
    fontFamily: typography.fontFamily.medium,
    color: colors.darkFont,
    fontSize: typography.fontSize.body,
    marginVertical: 12,
    marginLeft: 8
  },
  iconWrapper: {
    width: 40,
    height: 40,
    padding: 10,
    borderRadius: 100,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardsWrapper: {
    alignItems: 'center',
  },
});
