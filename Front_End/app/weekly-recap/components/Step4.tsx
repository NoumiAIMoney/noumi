import HorizontalCard from '@/components/HorizontalCard';
import { getSpendingCategories } from '@/src/api/spending';
import { colors, typography } from '@/src/theme';
import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import CarIcon from '@/assets/icons/car.svg'

type SpendingCategory = {
  category_name: string;
  amount: number;
  month: string;
};

export default function Step4() {
  const [categories, setCategories] = useState<SpendingCategory[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getSpendingCategories();

        setCategories(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  if (!categories) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Your top three spending categories this week:</Text>
      <View style={styles.cardsWrapper}>
        {categories.slice(0, 3).map((category, index) => (
          <HorizontalCard
            key={index}
            title={category.category_name || 'N/A'}
            white={true}
            icon={
              <View style={styles.iconWrapper}>
                <CarIcon width={24} height={24} fill="none" stroke={colors.white} />
              </View>
            }
            amount={String(category.amount)}
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
    marginBottom: 40,
    marginLeft: 8,
    marginRight: 24
  },
  iconWrapper: {
    width: 39.09,
    height: 40,
    padding: 10,
    borderRadius: 100,
    backgroundColor: '#B4698F',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8
  },
  cardsWrapper: {
    alignItems: 'center',
  },
});

