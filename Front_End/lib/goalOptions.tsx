import { colors } from '@/src/theme';
import AirplaneIcon from '../assets/icons/airplane.svg';
import CarIcon from '../assets/icons/car.svg';
import CardsIcon from '../assets/icons/cards.svg';
import CustomIcon from '../assets/icons/custom.svg';
import DollarIcon from '../assets/icons/dollar.svg';
import HouseIcon from '../assets/icons/house.svg';
import InvestIcon from '../assets/icons/invest.svg';
import StudentIcon from '../assets/icons/student.svg';

export interface GoalOption {
  id: string;
  label: string;
  icon: React.ReactElement;
}

export const goalOptions: GoalOption[] = [
  {
    id: 'cards',
    label: 'Pay off Credit Card',
    icon: (
      <CardsIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.darkFont}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'travel',
    label: 'Travel Fund',
    icon: (
      <AirplaneIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.darkFont}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'house',
    label: 'Buy a House',
    icon: (
      <HouseIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.darkFont}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'car',
    label: 'Buy a Car',
    icon: (
      <CarIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.darkFont}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'emergency',
    label: 'Build Emergency Fund',
    icon: (
      <DollarIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.darkFont}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'student',
    label: 'Pay Off Student Loan',
    icon: (
      <StudentIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.darkFont}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'investing',
    label: 'Investing Fund',
    icon: (
      <InvestIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.darkFont}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'custom',
    label: 'Custom Goal',
    icon: (
      <CustomIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.darkFont}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  }
];
