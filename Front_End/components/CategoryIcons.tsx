import BankFeesIcon from '@/assets/icons/categories/Bank_Fees.svg';
import CashAdvanceIcon from '@/assets/icons/categories/Cash_Advance.svg';
import CoffeeCupIcon from '@/assets/icons/categories/CoffeeCup.svg';
import EntertainmentIcon from '@/assets/icons/categories/Entertainment.svg';
import FoodDrinkIcon from '@/assets/icons/categories/Food&Drink.svg';
import HealthcareIcon from '@/assets/icons/categories/Healthcare.svg';
import HomeImprovementIcon from '@/assets/icons/categories/Home_Improvement.svg';
import IncomeIcon from '@/assets/icons/categories/Income.svg';
import InterestIcon from '@/assets/icons/categories/Interest.svg';
import InvestmentsIcon from '@/assets/icons/categories/Investments.svg';
import PaymentIcon from '@/assets/icons/categories/Payment.svg';
import RentUtilitiesIcon from '@/assets/icons/categories/Rent&Utilities.svg';
import ShoppingIcon from '@/assets/icons/categories/Shopping.svg';
import TaxesIcon from '@/assets/icons/categories/Taxes.svg';
import TransferIcon from '@/assets/icons/categories/Transfer.svg';
import TransportationIcon from '@/assets/icons/categories/Transportation.svg';
import TravelIcon from '@/assets/icons/categories/Travel.svg';
import UncategorizedIcon from '@/assets/icons/categories/Uncategorized.svg';
import { colors } from '@/src/theme';
import { JSX } from 'react';

export const categoryIcons: Record<string, JSX.Element> = {
  'Bank Fees': <BankFeesIcon width={24} height={24} color={colors.white} />,
  'Cash Advance': <CashAdvanceIcon width={24} height={24} color={colors.white} />,
  'Coffee Shops': <CoffeeCupIcon width={24} height={24} color={colors.white} />,
  'Entertainment': <EntertainmentIcon width={24} height={24} color={colors.white} />,
  'Food & Drink': <FoodDrinkIcon width={24} height={24} color={colors.white} />,
  'Healthcare': <HealthcareIcon width={24} height={24} color={colors.white} />,
  'Home Improvement': <HomeImprovementIcon width={24} height={24} color={colors.white} />,
  'Income': <IncomeIcon width={24} height={24} color={colors.white} />,
  'Interest': <InterestIcon width={24} height={24} color={colors.white} />,
  'Investments': <InvestmentsIcon width={24} height={24} color={colors.white} />,
  'Payment': <PaymentIcon width={24} height={24} color={colors.white} />,
  'Rent & Utilities': <RentUtilitiesIcon width={24} height={24} color={colors.white} />,
  'Shopping': <ShoppingIcon width={24} height={24} color={colors.white} />,
  'Taxes': <TaxesIcon width={24} height={24} color={colors.white} />,
  'Transfer': <TransferIcon width={24} height={24} color={colors.white} />,
  'Transportation': <TransportationIcon width={24} height={24} color={colors.white} />,
  'Travel': <TravelIcon width={24} height={24} color={colors.white} />,
  'Uncategorized': <UncategorizedIcon width={24} height={24} color={colors.white} />,
};
