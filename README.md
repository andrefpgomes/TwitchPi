# TwitchPi

Projeto para Raspberry Pi 3B/3B+ para controlar remotamente uma sessão Chromium dedicada ao Twitch através de uma interface web local.

## Funcionalidades

- Seleção do canal Twitch.
- Iniciar a visualização da live.
- Parar a visualização sem parar o serviço web.
- Perfil Chromium persistente para manter a sessão Twitch.
- Login Twitch aberto diretamente no Chromium.
- Favoritos de canais.
- Interface adaptada a telemóvel e computador.
- Compatível com uma instalação existente do Pi-hole, sem alterar a configuração do Pi-hole.

## Instalação/update por USB

1. Copie a pasta do projeto para uma pen USB.
2. Na Raspberry, abra a pasta do projeto.
3. Execute:

```bash
sudo bash update.sh
```

O update substitui apenas os ficheiros da aplicação e reinicia `twitch-pi.service`. Não substitui `state.json`, `config.env` ou o perfil Chromium existente.

## Interface web

Por defeito:

```text
http://IP_DA_RASPBERRY:8765
```

## Raspberry Pi

O projeto foi preparado para Raspberry Pi 3B com Debian 13/Trixie e Chromium instalado.

## Estrutura

```text
TwitchPi/
├── server.py
├── update.sh
├── web/
│   ├── index.html
│   ├── app.js
│   └── style.css
└── README.md
```

## Nota

O projeto controla a reprodução através de um navegador Chromium local. A aplicação não recebe nem armazena a palavra-passe da conta Twitch.
