import CardsIcon from '../../../assets/icons/cards.svg';
import AirplaneIcon from '../../../assets/icons/airplane.svg';
import { colors } from '@/src/theme';

export const goalOptions = [
  {
    id: 'cards',
    label: 'Pay off Credit Card',
    icon: (
      <CardsIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.primaryPurple}
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
        stroke={colors.primaryPurple}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'house',
    label: 'Buy a House',
    icon: (
      <AirplaneIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.primaryPurple}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'car',
    label: 'Buy a Car',
    icon: (
      <AirplaneIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.primaryPurple}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'emergency',
    label: 'Build Emergency Fund',
    icon: (
      <AirplaneIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.primaryPurple}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'student',
    label: 'Pay Off Student Loan',
    icon: (
      <AirplaneIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.primaryPurple}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'investing',
    label: 'Investing Fund',
    icon: (
      <AirplaneIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.primaryPurple}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  },
  {
    id: 'custom',
    label: 'Custom Goal',
    icon: (
      <AirplaneIcon
        width={24}
        height={24}
        fill="none"
        stroke={colors.primaryPurple}
        strokeWidth={1.5}
        color={colors.darkFont}
      />
    ),
  }
];
