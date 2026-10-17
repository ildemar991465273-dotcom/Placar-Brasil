# GolUp 2.7 — Android

Projeto Android com a interface completa do GolUp 2.7 (`app/src/main/assets/index.html`).

## Como obter APK usando somente o celular

1. Acesse a aba **Actions** deste repositório.
2. Abra **Gerar APK GolUp**, selecione a execução mais recente.
3. Se a execução tiver sucesso (verde), baixe o artefato **GolUp-Android-APK**.
4. Extraia o ZIP e instale o arquivo `app-debug.apk` no Android.

O fluxo utiliza GitHub Actions/Gradle e gera APK de **teste**, não de lançamento assinado para Play Store.

## Limitações atuais

- Resultados reais exigem API-Football e backend online configurados.
- Chat entre usuários depende de autenticação e servidor.
- Previsões premium são demonstrativas, não análises ou previsões verificadas.
- Pagamentos dos fogos e planos Premium ainda não foram integrados.
- Escudos são ilustrativos e o projeto inclui interface de demonstração offline.
