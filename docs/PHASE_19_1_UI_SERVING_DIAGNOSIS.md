# DIAGNÓSTICO: SERVIÇO DA UI (PHASE 19.1)

## 1. Qual arquivo serve `/ui`?
O backend (FastAPI) em `app.py` serve a rota `/ui` a partir da variável `FRONTEND_DIR`.
O valor dessa variável está definido como:
`BASE_DIR / "src" / "openjarvis" / "server" / "static"`
O arquivo servido é o `index.html` contido nessa pasta, juntamente com seus assets.

## 2. Origem do Build Vite
A pasta `src/openjarvis/server/static/` contém arquivos minificados que não devem ser editados manualmente. Eles são o resultado de um processo de build (empacotamento).
O código fonte verdadeiro (onde as telas, botões e textos são programados em React) reside na pasta `frontend/`.

## 3. Destino do Build e Como o Docker Serve
O `vite.config.ts` do frontend direciona sua saída (`outDir`) para `../src/openjarvis/server/static`.
Quando o Docker da TokyoOS faz o boot, ele copia o diretório inteiro do projeto, e o FastAPI monta `/ui` direto sobre os estáticos minificados presentes na pasta `src/openjarvis/server/static`.

## 4. Por Que a Tela Parecia OpenJarvis?
Durante as Fases 14 a 19, toda a fusão entre a TokyoOS e a OpenJarvis ocorreu apenas na camada de **Backend** e de **Agentes** (Python). 
A UI em React não havia sido modificada para refletir essas mudanças arquiteturais. O layout antigo e estático do OpenJarvis ainda imperava no frontend, escondendo os poderosos módulos da TokyoOS por trás de uma casca inalterada.

## 5. Arquivos Que Serão Alterados
Para alinhar a UI à verdade arquitetural:
- `frontend/index.html` (Mudar título de aba e meta-tags).
- `frontend/src/App.tsx` (ou componente principal de layout).
- `frontend/src/components/...` (Painéis laterais, Cabeçalho).
- Novos componentes para consumir endpoints FastAPI da TokyoOS (`/tokyo/dashboard/...`).
- E no final, a execução de `npm run build` sobreescreverá a pasta `static` obsoleta.
