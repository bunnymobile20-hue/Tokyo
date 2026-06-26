"""
TokyoOS Business AI Employees (CFO, COO, Estoque).
Custom agents built on OpenJarvis BaseAgent.
"""
from __future__ import annotations
import os
import json
import logging
from typing import Any, Optional
from openjarvis.agents._stubs import BaseAgent, AgentContext, AgentResult
from openjarvis.core.registry import AgentRegistry

logger = logging.getLogger("tokyoos.agents")

def get_mock_status() -> bool:
    return os.getenv("MOCK_DATA_ENABLED", "false").lower() in ("true", "1", "yes")

@AgentRegistry.register("tokyo_cfo")
class TokyoCfoAgent(BaseAgent):
    """Tokyo CFO Agent - handles financial analysis, cash flow, DRE, break-even."""
    agent_id = "tokyo_cfo"
    
    def run(self, input: str, context: Optional[AgentContext] = None, **kwargs: Any) -> AgentResult:
        mock_enabled = get_mock_status()
        
        if mock_enabled:
            # realistic mock data explicitly marked as MOCK/DEMO
            data_summary = (
                "=== [MOCK/DEMO FINANCIAL DATA] ===\n"
                "Demonstrativo do Resultado do Exercício (DRE):\n"
                "  - Receita Bruta MTD: R$ 150.000,00 [MOCK]\n"
                "  - Deduções/Impostos MTD: R$ 7.500,00 [MOCK]\n"
                "  - Receita Líquida MTD: R$ 142.500,00 [MOCK]\n"
                "  - Custos (COGS) MTD: R$ 65.000,00 [MOCK]\n"
                "  - Lucro Bruto MTD: R$ 77.500,00 [MOCK]\n"
                "  - Despesas Fixas MTD: R$ 32.000,00 [MOCK]\n"
                "  - Despesas Variáveis MTD: R$ 15.000,00 [MOCK]\n"
                "  - Resultado Operacional (Lucro) MTD: R$ 30.500,00 [MOCK]\n"
                "\n"
                "Fluxo de Caixa:\n"
                "  - Saldo Inicial: R$ 45.000,00 [MOCK]\n"
                "  - Entradas MTD: R$ 150.000,00 [MOCK]\n"
                "  - Saídas MTD: R$ 125.000,00 [MOCK]\n"
                "  - Saldo de Caixa Atual: R$ 70.000,00 [MOCK]\n"
                "  - Contas a Receber: R$ 85.000,00 [MOCK]\n"
                "  - Contas a Pagar: R$ 35.000,00 [MOCK]\n"
            )
        else:
            # Production: try to load from real Siberian Connector if enabled
            from siberian_connector.service import fetch_finance_summary, is_configured
            if is_configured():
                fin = fetch_finance_summary()
                if fin.get("success"):
                    data_summary = json.dumps(fin.get("data", {}), indent=2)
                else:
                    data_summary = "Erro ao buscar dados do Siberian ERP."
            else:
                data_summary = "Não encontrei dados reais suficientes para uma análise completa. Posso fazer uma análise parcial com os dados disponíveis e listar quais informações precisam ser conectadas."
                return AgentResult(content=data_summary, turns=1)
                
        system_prompt = (
            "Você é a Tokyo CFO, a diretora financeira e analista oficial do GrupsBunny.\n"
            "Seu objetivo é analisar os dados financeiros providos (DRE, Fluxo de Caixa, Balanços) e propor "
            "sugestões práticas de corte de despesas, metas, controle de contas a pagar e saúde geral do caixa.\n"
            "Se os dados forem marcados como MOCK/DEMO, você DEVE explicitamente alertar o usuário no início "
            "de sua resposta com uma mensagem clara destacando que está usando dados de demonstração/teste.\n"
            "Responda em português com clareza, objetividade e precisão."
        )
        
        prompt = f"Dados Financeiros para Análise:\n{data_summary}\n\nInstrução do usuário: {input}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = self._generate(messages)
            content = result.get("content", "")
        except Exception as e:
            logger.warning(f"Cognitive engine offline, using template analysis: {e}")
            if mock_enabled:
                content = (
                    "Com base no DRE e Fluxo de Caixa da Bunny Dreams MTD:\n"
                    "1. A Receita Líquida está em R$ 142.500,00 [MOCK], com Custos (COGS) de R$ 65.000,00 [MOCK], gerando Lucro Bruto de R$ 77.500,00 [MOCK].\n"
                    "2. As despesas operacionais somam R$ 47.000,00 [MOCK], resultando em Lucro Operacional de R$ 30.500,00 [MOCK].\n"
                    "3. Recomendação do dia: O caixa atual está saudável em R$ 70.000,00 [MOCK], mas há R$ 35.000,00 em contas a pagar. Recomendo provisionar o pagamento das despesas fixas hoje e acompanhar as contas a receber (R$ 85.000,00 [MOCK])."
                )
            else:
                content = f"Erro ao gerar análise financeira real: {e}"
        
        if mock_enabled:
            content = "⚠️ **[DEMO/MOCK DATA ACTIVE]** - A análise abaixo foi feita utilizando dados de demonstração.\n\n" + content
            
        return AgentResult(content=content, turns=1)

@AgentRegistry.register("tokyo_coo")
class TokyoCooAgent(BaseAgent):
    """Tokyo COO Agent - manages operational tasks, checklists, store issues, and efficiency."""
    agent_id = "tokyo_coo"
    
    def run(self, input: str, context: Optional[AgentContext] = None, **kwargs: Any) -> AgentResult:
        mock_enabled = get_mock_status()
        
        if mock_enabled:
            data_summary = (
                "=== [MOCK/DEMO OPERATIONAL DATA] ===\n"
                "Status das Lojas:\n"
                "  1. Loja Riverside (Teresina):\n"
                "     - Execução do Checklist diário: 92% [MOCK]\n"
                "     - Pendências: Reposição da vitrine clássica de inverno pendente [MOCK]\n"
                "     - Problemas reportados: Ar condicionado da entrada com barulho [MOCK]\n"
                "  2. Loja Teresina Shopping (Teresina):\n"
                "     - Execução do Checklist diário: 88% [MOCK]\n"
                "     - Pendências: Nenhuma pendência crítica [MOCK]\n"
                "     - Problemas: Nenhum [MOCK]\n"
            )
        else:
            data_summary = "Não encontrei dados reais de operações no momento."
            return AgentResult(content=data_summary, turns=1)
            
        system_prompt = (
            "Você é a Tokyo COO, a diretora de operações do GrupsBunny.\n"
            "Seu trabalho é monitorar as rotinas das lojas, checklists diários, pendências operacionais "
            "e organizar tarefas para as colaboradoras de cada unidade.\n"
            "Se os dados forem mock/demo, alerte o usuário no início de sua resposta.\n"
            "Responda em português."
        )
        
        prompt = f"Dados Operacionais:\n{data_summary}\n\nInstrução do usuário: {input}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = self._generate(messages)
            content = result.get("content", "")
        except Exception as e:
            logger.warning(f"Cognitive engine offline, using template analysis: {e}")
            if mock_enabled:
                content = (
                    "Com base nos dados operacionais das lojas GrupsBunny:\n"
                    "1. Riverside (Teresina): Checklist diário em 92% [MOCK]. Reposição de vitrine de inverno pendente. Ar condicionado da entrada precisa de manutenção.\n"
                    "2. Teresina Shopping: Checklist diário em 88% [MOCK]. Nenhuma ocorrência grave reportada.\n"
                    "Recomendação do dia: Solicitar técnico para o ar condicionado da Riverside e cobrar equipe sobre a vitrine clássica de inverno."
                )
            else:
                content = f"Erro ao gerar análise operacional real: {e}"
        
        if mock_enabled:
            content = "⚠️ **[DEMO/MOCK DATA ACTIVE]**\n\n" + content
            
        return AgentResult(content=content, turns=1)

@AgentRegistry.register("tokyo_estoque")
class TokyoEstoqueAgent(BaseAgent):
    """Tokyo Stock/Inventory Agent - manages ABC curve, low stock alerts, and purchase requests."""
    agent_id = "tokyo_estoque"
    
    def run(self, input: str, context: Optional[AgentContext] = None, **kwargs: Any) -> AgentResult:
        mock_enabled = get_mock_status()
        
        if mock_enabled:
            data_summary = (
                "=== [MOCK/DEMO INVENTORY DATA] ===\n"
                "Itens Críticos (Abaixo do estoque mínimo ou zerados):\n"
                "  - SKU BD-DRESS-01 (Vestido Bunny Classic): Estoque 2 | Mínimo 10 [MOCK]\n"
                "  - SKU BD-TSHIRT-05 (Camiseta Bunny Logo): Estoque 0 | Mínimo 15 [MOCK]\n"
                "Curva ABC de Vendas:\n"
                "  - Classe A (70% do faturamento): Vestido Bunny Classic (BD-DRESS-01), Calça Skinny (BD-JEANS-02) [MOCK]\n"
                "  - Classe B (20%): Camisa Linho (BD-SHIRT-03) [MOCK]\n"
                "  - Classe C (10%): Meia Estampada (BD-SOCK-04) [MOCK]\n"
                "Valores Totais:\n"
                "  - Total de Itens em estoque: 4.500 unidades [MOCK]\n"
                "  - Valor total investido em estoque: R$ 180.000,00 [MOCK]\n"
            )
        else:
            from siberian_connector.service import fetch_stock_summary, is_configured
            if is_configured():
                stock = fetch_stock_summary()
                if stock.get("success"):
                    data_summary = json.dumps(stock.get("data", {}), indent=2)
                else:
                    data_summary = "Erro ao ler estoque real do Siberian ERP."
            else:
                data_summary = "Não encontrei dados reais de estoque no momento."
                return AgentResult(content=data_summary, turns=1)
                
        system_prompt = (
            "Você é a Tokyo Estoque, a especialista em gestão de inventário e compras do GrupsBunny.\n"
            "Seu papel é analisar rupturas de estoque, curva ABC, sugerir reabastecimento de produtos críticos "
            "e manter a margem otimizada com foco em produtos de alta rotatividade.\n"
            "Se os dados forem mock/demo, alerte o usuário no início de sua resposta.\n"
            "Responda em português."
        )
        
        prompt = f"Dados de Estoque:\n{data_summary}\n\nInstrução do usuário: {input}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = self._generate(messages)
            content = result.get("content", "")
        except Exception as e:
            logger.warning(f"Cognitive engine offline, using template analysis: {e}")
            if mock_enabled:
                content = (
                    "Com base no relatório de estoque da Bunny Dreams:\n"
                    "1. Itens críticos (abaixo do mínimo): SKU BD-DRESS-01 (Vestido Bunny Classic) com apenas 2 unidades (mínimo 10) [MOCK]. SKU BD-TSHIRT-05 (Camiseta Bunny Logo) zerada [MOCK].\n"
                    "2. Curva ABC: Vestido Bunny Classic e Calça Skinny representam os produtos Classe A mais relevantes do faturamento.\n"
                    "Recomendação do dia: Iniciar pedido de compra de 15 unidades de BD-DRESS-01 e 20 unidades de BD-TSHIRT-05 para reestabelecer o estoque de segurança."
                )
            else:
                content = f"Erro ao gerar análise de estoque real: {e}"
        
        if mock_enabled:
            content = "⚠️ **[DEMO/MOCK DATA ACTIVE]**\n\n" + content
            
        return AgentResult(content=content, turns=1)
