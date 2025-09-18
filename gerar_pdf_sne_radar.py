from fpdf import FPDF
import textwrap

# Configurações do PDF
pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.set_auto_page_break(auto=True, margin=15)

# Cores (laranja forte e preto)
laranja_r = 237
laranja_g = 146
laranja_b = 30  # RGB aproximado para laranja forte

# Adiciona a capa
pdf.add_page()
pdf.set_font('Helvetica', 'B', 24)

# Capa: Título e elementos visuais
pdf.set_text_color(laranja_r, laranja_g, laranja_b)
pdf.cell(0, 10, 'SNE Radar', ln=True, align='C')
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(0, 10, 'SISTEMA NEURAL ESTRATÉGICO', ln=True, align='C')

# Adiciona o subtítulo
pdf.set_font('Helvetica', 'I', 12)
pdf.set_text_color(0, 0, 0)  # Preto para melhor legibilidade
pdf.cell(0, 10, 'Plataforma de Análise de Mercado em Tempo Real', ln=True, align='C')

# Adiciona o rodapé
pdf.set_y(-15)
pdf.set_font('Helvetica', 'I', 10)
pdf.set_text_color(150, 150, 150)
pdf.cell(0, 10, 'Desenvolvido por Renan Melo | sne-radar.com', align='C')

# Adiciona as seções do conteúdo
secoes = {
    "1. Visão Geral": 
        "O SNE Radar é uma plataforma avançada de análise de mercado em tempo real, projetada para traders, investidores e instituições. "
        "Combina leitura intuitiva com análise de dados, oferecendo insights precisos e estratégicos.\n\n"
        "Diferenciais:\n"
        "- Visualização única da estrutura de mercado\n"
        "- Integração com múltiplas APIs (Binance, CoinGecko, Bybit, KuCoin, MEXC, BingX)\n"
        "- Dados mock ultra-realistas em caso de falha de APIs\n"
        "- Estratégias adaptativas multi-timeframe\n"
        "- Comunicação em tempo real via WebSocket",
    
    "2. Arquitetura do Sistema": 
        "- Backend: Flask + Flask-SocketIO\n"
        "- Banco de Dados: SQLAlchemy\n"
        "- Processamento: Threading assíncrono\n"
        "- Segurança: Hash bcrypt, sanitização de inputs, rate limiting\n"
        "- Fallback Inteligente: múltiplas fontes de dados, cache local e dados mock ultra-realistas\n"
        "- Interface: Web-based, gráficos e radar visual",
    
    "3. Funções Principais": 
        "- buscar_dados_mercado(symbol, interval, limit) -> fallback entre APIs, cache e mock\n"
        "- processar_dados_brutos(df) -> indicadores técnicos (EMA8, EMA21, SMA200, RSI14)\n"
        "- analisar_simbolo_estrategico(symbol, df, ruptura, percentual) -> análise integrada com módulos de impulso, densidade gravitacional e memória neural\n"
        "- gerar_estrategia_trading(...) -> tendências, volume, rupturas\n"
        "- executar_ciclo_analise() -> loop de processamento paralelo, alertas e WebSocket",
    
    "4. Tecnologias Envolvidas": 
        "- Python, Flask, Flask-SocketIO\n"
        "- SQLAlchemy, Threading, Cache Inteligente\n"
        "- APIs: Binance, CoinGecko, Bybit, KuCoin, MEXC, BingX\n"
        "- Deploy: Render / Cloudflare / Cloud\n"
        "- CI/CD: GitHub Actions",
    
    "5. Diferenciais Competitivos": 
        "- Leitura baseada em Campos Magnéticos\n"
        "- Radar visual único e intuitivo\n"
        "- Estratégias adaptativas multi-timeframe\n"
        "- Mock ultra-realista mantém credibilidade do sistema\n"
        "- Escalabilidade para milhares de usuários em tempo real\n"
        "- Monetização por tiers (Free, Pro, Institutional)",
    
    "6. Modelo de Negócio": 
        "- Free Tier: 100 calls/dia\n"
        "- Pro Tier: 1.000 calls/dia, relatórios avançados\n"
        "- Institutional Tier: 10.000 calls/dia, integrações e suporte premium\n"
        "- Receita recorrente por assinatura\n"
        "- Potencial de parcerias com corretoras e fundos",
    
    "7. Roadmap de Expansão": 
        "Ano\tObjetivo\n"
        "2025\tLançamento SNE Radar, versão Pro e primeiros clientes\n"
        "2026\tDashboard refinado, API pública\n"
        "2027\tEscala global, integração institucional\n"
        "2028\tExpansão global consolidada, AI simbólica aplicada\n"
        "2030\tIPO SNE-T, valuation estimado: $1.5B",
    
    "8. Valuation Detalhado": 
        "- Valuation Atual (2025): $1.2M\n"
        "- Curto Prazo (2026): $5M\n"
        "- Médio Prazo (2028): $50M\n"
        "- IPO Target (2030): $1.5B\n"
        "- Crescimento guiado por expansão global, novos módulos e integrações institucionais",
    
    "9. Custos de Manutenção": 
        "- Infraestrutura Cloud: $500/mês\n"
        "- APIs & Dados: $300/mês\n"
        "- Servidores & Segurança: $200/mês\n"
        "- Marketing & Growth: $1.000/mês\n"
        "- Equipe Técnica & Suporte: $2.000/mês\n\n"
        "Resumo:\n"
        "- Custo mensal: $4.000\n"
        "- Custo anual: $48.000",
    
    "10. Receita por Tiers": 
        "- Free Tier: base massiva de usuários, gateway de upsell\n"
        "- Pro Tier: $29/mês, 10.000 usuários alvo -> $3,5M/ano\n"
        "- Institutional Tier: $999/mês, 500 clientes alvo -> $6M/ano\n\n"
        "ARR estimada: $10M+",
    
    "11. Potencial de Mercado": 
        "- TAM: $50B (Mercado Global de Análise Financeira)\n"
        "- SAM: $10B (Mercado Crypto & Trading)\n"
        "- SOM: $150M (Meta captável pelo SNE Radar)\n\n"
        "Estratégia: Penetração global focada em nichos institucionais, posicionamento premium e escalável.",
    
    "12. Conclusão": 
        "O SNE Radar, desenvolvido por Renan Melo, é uma solução profissional, robusta e escalável, "
        "combinando análise de mercado visual, estratégia adaptativa e tecnologia avançada.\n\n"
        "Pronto para:\n"
        "- Parcerias institucionais\n"
        "- Expansão global\n"
        "- Investimento estratégico\n"
        "- IPO em 2030"
}

# Adiciona cada seção
for titulo, texto in secoes.items():
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(laranja_r, laranja_g, laranja_b)
    pdf.cell(0, 10, titulo, ln=True)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(0, 0, 0)  # Preto para melhor legibilidade
    
    # Quebra de linha e formatação do texto
    for linha in texto.split('\n'):
        if linha.strip() == '':
            pdf.ln(5)
        else:
            pdf.multi_cell(0, 7, linha)
    
    # Adiciona o rodapé em cada página
    pdf.set_y(-15)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, 'Desenvolvido por Renan Melo | sne-radar.com', align='C')

# Salva o PDF
pdf_output_path = 'sne_radar_executivo.pdf'
pdf.output(pdf_output_path)

print(f"✅ PDF gerado com sucesso: {pdf_output_path}")
print("📄 Arquivo salvo no diretório atual")
