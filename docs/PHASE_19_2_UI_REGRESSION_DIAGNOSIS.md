# DIAGNÓSTICO: REGRESSÃO DE UI (PHASE 19.2)

## 1. Qual era o layout original da TokyoOS?
Antes da adoção pesada do OpenJarvis como base, a TokyoOS possuía uma UI centralizada (`/ui`) que priorizava a assistente de voz nativa, os cards empresariais (GrupsBunny, Bunny Dreams, Bunny Siberian) e os módulos de finanças/vendas em uma interface visualmente limpa e conectada aos seus próprios endpoints. 

## 2. Quais arquivos representavam a UI original?
Nas fases iniciais, antes da fusão (Phase 13 e anteriores), a TokyoOS utilizava templates puros, com injeções pontuais. Havia o `ui/` original que foi mesclado com o repositório OpenJarvis (`frontend/`).

## 3. Quais componentes foram substituídos por OpenJarvis?
Durante as Fases 14 a 19.1, focamos em encapsular o backend do OpenJarvis, mas no frontend adotamos o repositório `frontend/` (um projeto React gigantesco focado em chat) inteiro, o que sobreescreveu a home page da TokyoOS com o layout de "Chatbot" do OpenJarvis.

## 4. Onde a voz ativa aparecia antes?
A voz era uma aba primária na home, com botão explícito de ativação e status do microfone.

## 5. Onde as empresas apareciam antes?
Havia cards das operações (Teresina, Riverside, etc.) e links rápidos para os dashboards de cada empresa.

## 6. Quais menus são reais e quais são falsos/scaffold?
- O menu de `Chat` (OpenJarvis Core) funciona (mas é secundário).
- Os menus adicionados na fase 19.1 (`DRE & Estoque`, `Siberian Read-Only`) apontavam para o componente `TokyoOSDashboard` que renderizava uma tela solta no meio da estrutura do OpenJarvis, criando a sensação de remendo.

## 7. Qual build está sendo servido?
A porta 8788 entrega o `src/openjarvis/server/static/index.html` compilado pelo Vite. O container continua servindo o frontend atual. O frontend atual é um "OpenJarvis renomeado", não a TokyoOS restaurada.

## CONLUSÃO DO DIAGNÓSTICO
O erro foi construir "por cima" do React do OpenJarvis, tentando disfarçá-lo de TokyoOS apenas trocando a barra lateral. A abordagem correta é construir a "Dashboard TokyoOS" como o painel principal (`/`), colocar a voz no centro, exibir as empresas de imediato, e relegar o "Chat OpenJarvis" para uma aba de "OpenJarvis Core".
