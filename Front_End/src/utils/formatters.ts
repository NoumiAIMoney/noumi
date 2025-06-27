export function formatDollarAmountsInText(text: string): string {
  return text.replace(/\$\d+(?:\.\d{2})?/g, match => {
    const number = parseFloat(match.replace('$', ''));
    if (isNaN(number)) return match; // Fallback in case parsing fails
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
