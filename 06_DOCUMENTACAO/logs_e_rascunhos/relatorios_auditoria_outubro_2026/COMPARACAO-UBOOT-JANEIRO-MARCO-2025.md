# Comparação do U-Boot de janeiro e março de 2025

Data: 02/10/2026. Somente leitura; nenhuma instalação, alteração de imagem ou acesso ao roteador.

## Conclusão

A diferença binária inicialmente registrada não corresponde a uma mudança demonstrada de funcionalidade. Comparando os 565.320 bytes do payload de U-Boot da versão 1.01.000027 com o início do dump OEM preservado, apenas 65 bytes diferem, distribuídos por 19 intervalos.

Todos os intervalos foram classificados:
- 32 bytes: SHA-256 do segmento PT_LOAD no cabeçalho;
- 33 bytes: textos de versão/data, identificação do build/toolchain e timestamp de um gzip.

Não foram encontradas diferenças fora desses intervalos. As regiões examinadas de bootm, source, handlers de rede, classificação de imagem e despacho do Failsafe são idênticas.

Isso sustenta que, para o código e os dados deste payload, não existe mudança funcional identificada que habilite Netconsole ou altere o boot ARM64. Não equivale a um teste de funcionamento do pacote completo.

## Evidências

Os dois ELF têm o mesmo segmento:
- offset: 0x12000;
- endereço: 0x4a400000;
- tamanho: 0x78048;
- fim: 0x4a478048.

Mudanças de texto:
- U-Boot 2016.01: Jan 17 2025 04:02:54 → Mar 11 2025 08:57:41;
- rodapé da página de recuperação: 25.01.17 → 25.03.11;
- identificador OEM: qca_oem-2036 → qca_oem-2262;
- string do toolchain: r0+14311-9a354fd0ab → r0+14315-60fc7c16ce.

O SHA-256 em 0x1070–0x108f corresponde, em ambos os arquivos, ao hash calculado do respectivo segmento PT_LOAD. Portanto essa mudança é explicada pelas diferenças de metadados do próprio segmento.

O gzip em 0x79e90, identificado como dtb_combined.bin, difere apenas no timestamp do cabeçalho. Seu conteúdo descomprimido é idêntico:
- 65.488 bytes;
- SHA-256: 06b05fb2521b79b34fd0ea666c5819a8dc7047900768032527fb01f77d7ac3bb.

Isso também esclarece por que a tentativa anterior de extrair um DTB cru em 0x520d0 era inválida: há uma coleção de DTBs comprimida em outra região. A coleção não foi extraída para disco nem interpretada como o DTB final entregue ao kernel nesta etapa.

As entradas e funções de tftpboot, tftpput, bootm, source e httpd têm os mesmos offsets e endereços nos dois U-Boots. Não foram encontrados os marcadores ncip, ncinport ou ncoutport em nenhum deles.

Regiões comparadas diretamente:
- bootm e auxiliares: offsets 0x1b780–0x1bbff;
- source: 0x1cf50–0x1d0bf;
- wrappers de rede: 0x24470–0x2451f;
- despacho de upload: 0x5c4b4–0x5c62b;
- classificação de imagem: 0x58cd4–0x58d17.

## Consequência prática

Não há ganho demonstrado para justificar substituir o U-Boot existente buscando Netconsole, TFTP ou solução da transição ARM64. TFTP e tftpput já existem no backup atual.

O pacote completo continua contendo instruções de gravação de componentes críticos. Sua aplicação não foi autorizada nem executada.

O arquivo da atualização tem SHA-256 b18c54aabfbad9da22245748e393e63f8b56467e011fac3bdba021f8a91103cc; o dump APPSBL preservado tem SHA-256 3d6281190512ba50b83eea1a2d6fca69f01da5bb390d52b601e762ce8f1df2fc.

Este documento complementa INSPECAO-FIRMWARE-101000027-2026-10-02.md sem modificar o relatório anterior.

