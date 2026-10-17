# GolUp — ativar jogos reais via football-data.org

1. Cadastre-se em https://www.football-data.org/client/register e obtenha sua chave de acesso. Consulte os limites e as competições cobertas pelo plano escolhido.
2. No Render, abra o serviço `golup-api` > Environment e adicione a variável `FOOTBALL_DATA_KEY` com sua chave como valor. Não divulgue a chave no GitHub ou chat.
3. Salve e faça redeploy da versão atual do repositório `main`.
4. Verifique o endereço público `https://golup-api.onrender.com/health`. Ele deve indicar `"provider": "football-data.org"`.
5. Teste `https://golup-api.onrender.com/api/fixtures?date=2026-10-17`. Se a data não tiver partidas cobertas, o servidor retorna `{"data":[]}`; teste também um dia com partidas em competições disponíveis.
6. Reinicie o GolUp. O mesmo endpoint de partidas continua compatível com a interface existente.

**Limites:** football-data.org não oferece todas as ligas do mundo no plano gratuito, e detalhes de narração e eventos de todas as partidas não estão implementados nessa alternativa. A opção `FOOTBALL_DATA_KEY` tem prioridade para partidas sobre a conta API-Football suspensa. Não confunda dados ausentes com jogos inventados.
