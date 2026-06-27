# CHECKPOINT DE ROLLBACK (PHASE 19.2)

## 1. Estado Atual da UI
A UI encontra-se como um chat do OpenJarvis renomeado para "TokyoOS". A tela principal abre diretamente no input de chat. Os menus adicionados ficaram amontoados na barra lateral apontando para a mesma rota (`/dashboard`) que agora possui todos os componentes (Energy, Traces, e os scaffolds da TokyoOS) injetados de forma mista, poluindo visualmente e descaracterizando a TokyoOS.

## 2. Arquivos do Frontend Afetados
Na Fase 19.1, os seguintes arquivos foram editados:
- `frontend/index.html`: Nome alterado.
- `frontend/src/components/Sidebar/Sidebar.tsx`: Menus laterais apontados para rotas fake/scaffold.
- `frontend/src/pages/DashboardPage.tsx`: Módulo `TokyoOSDashboard` foi injetado.
- `frontend/src/components/Dashboard/TokyoOSDashboard.tsx`: Componente criado para consumir `/tokyo/dashboard/*`.

## 3. Rotas Impactadas
A rota `/dashboard` do frontend foi sobrecarregada para tentar hospedar todas as informações das empresas, estoque, DRE e siberian read-only. O resto da aplicação continuou puramente OpenJarvis (Chat, Agents, Data Sources).

## 4. O Que Sumiu da TokyoOS
- A presença centralizada da **Voz (Tokyo Voice)** com status e gravação.
- Os cartões limpos e bonitos para cada unidade de negócio (GrupsBunny, Bunny Dreams, Bunny Siberian).
- A clareza de que o usuário está no Command Center da empresa; o sistema parece apenas uma interface de prompt genérico de IA.

## 5. Plano de Rollback e Restauração
- Ao invés de usar `ChatPage.tsx` como home page (`/`), usaremos uma nova `HomePage.tsx` nativa da TokyoOS que conterá os painéis empresariais, a voz e o status.
- O OpenJarvis Chat será movido para uma sub-rota dedicada (`/openjarvis-core`).
- A `Sidebar.tsx` será limpa de "menus fake" e conterá botões funcionais para as seções reais do Command Center, priorizando a verdadeira hierarquia da TokyoOS.
