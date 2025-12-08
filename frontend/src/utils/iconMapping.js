/**
 * Mapeamento de Emojis para Ícones Lucide
 * Centraliza todas as substituições de emojis por ícones SVG
 */

// Importar apenas os ícones que serão usados (tree-shaking)
import {
  TrendingUp,
  TrendingDown,
  ArrowRight,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Activity,
  Zap,
  Target,
  DollarSign,
  Shield,
  RefreshCw,
  Loader2,
  BarChart3,
  LineChart,
  MapPin,
  Clock,
  Minus,
  ChevronsUp,
  ChevronsDown
} from 'lucide-vue-next'

/**
 * Mapeamento direto: emoji → componente de ícone
 */
export const emojiToIcon = {
  // Direções e Tendências
  '📈': TrendingUp,
  '📉': TrendingDown,
  '⬆️': ArrowUpRight,
  '⬇️': ArrowDownRight,
  '➡️': ArrowRight,
  '↗': ArrowUpRight,
  '↘': ArrowDownRight,
  
  // Status e Validação
  '✅': CheckCircle2,
  '⚠️': AlertTriangle,
  '❌': XCircle,
  '✗': XCircle,
  
  // Ações e Conceitos
  '🔥': Activity,
  '⚡': Zap,
  '🎯': Target,
  '💰': DollarSign,
  '🛡️': Shield,
  '📊': BarChart3,
  '📍': MapPin,
  '🔄': RefreshCw,
  '⏳': Loader2,
  '🕐': Clock,
  
  // Sinais de Trading
  '🐂': ChevronsUp,      // Touro (Bull) → Seta dupla para cima
  '🐻': ChevronsDown,    // Urso (Bear) → Seta dupla para baixo
}

/**
 * Mapeamento por contexto (quando o mesmo emoji pode ter significados diferentes)
 */
export const contextIconMap = {
  // Sinais de Trading
  buy: TrendingUp,
  sell: TrendingDown,
  long: TrendingUp,
  short: TrendingDown,
  neutral: Minus,
  
  // Status
  success: CheckCircle2,
  warning: AlertTriangle,
  error: XCircle,
  info: AlertTriangle,
  
  // Ações
  refresh: RefreshCw,
  loading: Loader2,
  update: RefreshCw,
  
  // Conceitos
  price: DollarSign,
  target: Target,
  protection: Shield,
  chart: BarChart3,
  location: MapPin,
  time: Clock,
}

/**
 * Função helper para obter ícone por emoji ou contexto
 */
export function getIcon(emojiOrContext) {
  // Se for emoji direto
  if (emojiToIcon[emojiOrContext]) {
    return emojiToIcon[emojiOrContext]
  }
  
  // Se for contexto
  if (contextIconMap[emojiOrContext?.toLowerCase()]) {
    return contextIconMap[emojiOrContext.toLowerCase()]
  }
  
  // Fallback
  return Activity
}

/**
 * Exportar todos os ícones para uso direto
 */
export {
  TrendingUp,
  TrendingDown,
  ArrowRight,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Activity,
  Zap,
  Target,
  DollarSign,
  Shield,
  RefreshCw,
  Loader2,
  BarChart3,
  LineChart,
  MapPin,
  Clock,
  Minus,
  ChevronsUp,
  ChevronsDown
}


