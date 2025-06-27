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
