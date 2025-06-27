export function formatDollarAmountsInText(text: string): string {
  return text.replace(/\$\d+(?:\.\d{2})?/g, match => {
    const number = parseFloat(match.replace('$', ''));
    if (isNaN(number)) return match;
    return `$${number.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  });
}

export function getCurrentWeekRange(): string {
  const today = new Date();
  const dayOfWeek = today.getDay();

  const diffToMonday = (dayOfWeek + 6) % 7;

  const monday = new Date(today);
  monday.setDate(today.getDate() - diffToMonday);

  const sunday = new Date(monday);
  sunday.setDate(monday.getDate() + 6);

  const format = (date: Date): string =>
    `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`;

  return `${format(monday)} - ${format(sunday)}`;
}


export const getPastFiveWeekRanges = (): string[] => {
  const weeks: string[] = [];
  const today = new Date();

  const day = today.getDay();
  const diffToMonday = day === 0 ? -6 : 1 - day;
  const currentMonday = new Date(today);
  currentMonday.setDate(today.getDate() + diffToMonday);

  for (let i = 0; i < 5; i++) {
    const start = new Date(currentMonday);
    start.setDate(currentMonday.getDate() - i * 7);
    const end = new Date(start);
    end.setDate(start.getDate() + 6);

    const format = (date: Date) => {
      const mm = String(date.getMonth() + 1).padStart(2, '0');
      const dd = String(date.getDate()).padStart(2, '0');
      return `${mm}/${dd}`;
    };

    weeks.push(`${format(start)} - ${format(end)}`);
  }

  return weeks;
};
