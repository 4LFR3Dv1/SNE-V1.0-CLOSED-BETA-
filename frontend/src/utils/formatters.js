/**
 * Formatters utility functions
 */

export function formatVolume(volume) {
  if (!volume || isNaN(volume)) return '--'
  if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B'
  if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M'
  if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K'
  return volume.toFixed(2)
}

export function formatPrice(price) {
  if (!price || isNaN(price)) return '--'
  const num = parseFloat(price)
  if (num >= 1000) {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  } else {
    return num.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }
}

