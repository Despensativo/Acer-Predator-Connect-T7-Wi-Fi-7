# OpenWrt 6.18 para Acer Predator Connect T7

## Estado

- [x] Conferir regras do projeto e espaço em disco interno.
- [x] Identificar imagens antigas e evidência: execução de kernel anterior não comprovada.
- [x] Clonar em WSL a árvore pública `perceival/openwrt-flint3`, commit `2365932733ca8ec3b346621d9cec2eb3df3b2cf3`, branch local `t7-ram-prototype`.
- [x] Criar perfil T7 somente initramfs, sem receita factory/sysupgrade, e copiar DTS candidato removendo MACs zerados e desabilitando PCIe não validado.
- [x] Corrigir mapa de RAM do DTS candidato com base no DTB capturado do T7 real: 1 GiB em `0x40000000`; o DTS genérico AP-MI01.6 tem 512 MiB e não serve como fonte para esse valor.
- [x] Reservar no DTS do protótipo as regiões fixas de bootloader, TrustZone, WCNSS, dumps, calibração e QCN9224 observadas no DTB do T7.
- [x] Comparar com `ipq5332.dtsi` efetivo do kernel 6.18.39 e eliminar reservas duplicadas/sobrepostas: o upstream já cobre bootloader, SBL, TZ, SMEM e WCSS. O DTS T7 passa a acrescentar apenas TZAPP, MLO e QCN9224 e redefine o nó de RAM existente.
- [x] Instalar feed público `packages` no WSL e baixar fontes necessárias; commits da árvore e feed preservados nos metadados de build.
- [x] Resolver falha inicial de `tools/tar`: o `configure` recusa usuário root. Árvore movida dentro do filesystem interno para `/home/builder/t7-openwrt-618`, propriedade do usuário não privilegiado `builder`, e build reiniciado.
- [x] Verificar configuração e compilação DTS/FIT.
- [x] Baixar dependências de build e compilar imagem initramfs (`make -j12`, saída 0).
- [x] Validar FIT, FDT, hashes dos componentes e ausência de artefato instalável.
- [x] Registrar limitações de boot/rádio/switch e próximos testes seguros em `BUILD_NOTES.md`.
- [ ] Confirmar boot somente em RAM no T7 real, após planejamento e autorização específica.
- [ ] Portar e validar switch QCA8386, rede, rádios, armazenamento NAND e recuperação antes de uma imagem instalável.
- [x] Confirmar estaticamente no APPSBL Acer a comparação do magic ARM64 e a chamada ao monitor seguro; `BOOT_PATH_STATIC.md` registra endereços e limites.
- [x] Conferir tamanho descomprimido do kernel 6.18.39 e ausência de sobreposição aritmética no mapa candidato de boot em RAM.
- [x] Revalidar a sonda U-Boot de rede já preparada e identificar que o diagnóstico v3 6.18.52 é o primeiro candidato de teste mais apropriado.
- [ ] Confirmar no hardware o caminho HTTP/source/rede com a sonda pendente, após aviso e autorização do usuário.
- [x] Pesquisar recuperação Acer de 2024 em diante: W6x stock, Vero W6m e W6x ubootmod, distinguindo IPs configurados manualmente de fallback automático; relatório em `06_DOCUMENTACAO/RECOVERY_ACER_2024PLUS_T7_2026-10-03.md`.
- [ ] Capturar passivamente ARP/TFTP na Ethernet correta durante entrada controlada no Failsafe do T7, após autorização de teste no aparelho; usar o resultado para evitar tentativas por adivinhação.

## Restrições

Nenhuma gravação no roteador. Nenhuma extração ou build no HD ExFAT. O T7 usa NAND e switch QCA8386; o porte Flint 3 tem eMMC e switch Realtek. Não tratar perfil ou FIT compilado como ROM instalável até haver validação de boot em RAM e hardware.
