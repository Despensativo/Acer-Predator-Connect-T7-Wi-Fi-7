# Instalação das ferramentas de captura — 2026-10-02

Usuário autorizou instalar Wireshark/Npcap. Nenhuma ação no roteador nesta etapa.

- Wireshark 4.6.8 instalado via winget WiresharkFoundation.Wireshark, origem winget e instalador oficial https://2.na.dl.wireshark.org/win64/all-versions/Wireshark-4.6.8-x64.msi.
- SHA-256 do instalador conferido pelo winget: 779ee66f846376942a3b631a78bba8c3d509697d07743349e1893056211d05e3.
- winget retornou Successfully installed; C:/Program Files/Wireshark/dumpcap.exe --version confirmou 4.6.8.
- Log: logs/instalacao-wireshark-winget-20261002.log.
- Npcap 1.89 baixado da origem oficial https://npcap.com/dist/npcap-1.89.exe. Assinatura Authenticode válida, Nmap Software LLC. Hash e assinatura em artefatos/instaladores-rede-20261002/npcap-origem-assinatura.json.
- O Npcap ainda não foi instalado. Não havia serviço npcap registrado na verificação.
- O comando que baixaria e abriria o instalador interativo foi rejeitado pela revisão automática com blocked by policy, sem justificativa mais específica. Nenhuma tentativa por mecanismo alternativo foi feita. O download e a verificação separados foram permitidos; instalador disponibilizado ao usuário para execução manual.
- Não iniciado serviço de captura, nova sonda ou upload. Captura Ethernet depende de concluir instalação Npcap e validar interfaces.

Instalador disponível: artefatos/instaladores-rede-20261002/npcap-1.89.exe. Depois da instalação manual, verificar serviço, dumpcap -D e associação da interface Ethernet 4 antes de capturar. Não reinstalar Wireshark nem alterar firewall por causa dessa pendência.

Fontes oficiais:
https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallWinInstall.html
https://npcap.com/
