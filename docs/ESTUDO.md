# Estudo na variante t950s_be311

## Ambiente observado

| Item | Valor |
| --- | --- |
| Modelo comercial | HY320 S8J |
| Plataforma | Amlogic T950S / TXHD2 |
| Identificador de dispositivo | `t950s_be311` |
| Android informado | 13, API 33, ARM de 32 bits |
| RAM | aproximadamente 1 GB |
| Kernel | família 5.15.119 |
| Patch declarado | 2023-04-05 |
| Integridade de boot | estado orange e verity desabilitado |
| Assinaturas do sistema | presença de chaves públicas de teste do AOSP |
| SELinux | não compilado no kernel |
| WebView observado | 131.0.6778.200 |

Existiam overlays de sistema/fabricante anteriores ao atendimento. As alterações usaram esses overlays e devolveram `/system` e `/vendor` a somente leitura. Não foi instalado bootloader, kernel ou ROM.

## Sequência de redução de exposição

1. Preservação de cópias privadas e inventário dos componentes necessários ao hardware.
2. Autorização da chave pública ADB do proprietário, sem transferir a chave privada.
3. Retirada da inicialização de um broker adicional de root, `jmsu --daemon`, e de rotinas de download/execução remota da família JM.
4. Remoção, para o usuário principal, de 27 pacotes dispensáveis. O launcher, players antigos e lojas paralelas entraram nessa revisão; a lista está em `data/packages.json` como histórico, não como comando de remoção em massa.
5. Neutralização dos scripts legados e isolamento das cópias de execução em `/data`; os originais ficaram privados para recuperação. Oito APKs antigos de reinstalação automática foram retirados depois de copiados e verificados por hash.
6. Bloqueios BADBOX/JM em hosts, DNS convencional e um IPv4 documentado.
7. Restrição de `su` e `run-as` para execução somente por root, modo `0700`; o SUID do `su` foi retirado. Os conteúdos dos binários não foram alterados.
8. Desativação, sem apagar os arquivos, de `com.droidlogic.updater`, `com.droidlogic.appinstall` e `com.koushikdutta.superuser`. O instalador padrão do Android foi preservado.
9. Restrição de solicitações de instalação de APKs em 18 aplicativos e de acesso amplo a arquivos em um app de mídia que foi mantido pelo proprietário.
10. Cinco restrições do kernel, firewall de entrada e manutenção TLS por uma porta IPv4 estável.

Desativar o atualizador do fabricante também impede atualizações automáticas legítimas por esse componente. Uma futura atualização precisa de revisão de procedência, compatibilidade e restauração. Esses três componentes não foram classificados como malware apenas por seus nomes ou privilégios.

## BADBOX e o alcance da evidência

A configuração preexistente continha uma URL em `jm.ttyunos.com`. O domínio pai aparece entre os indicadores públicos da pesquisa [BADBOX 2.0 da HUMAN Security](https://www.humansecurity.com/learn/blog/satori-threat-intelligence-disruption-badbox-2-0/). Isso foi tratado como **indicador estático**, sem atribuir autoria da configuração ou afirmar participação ativa da unidade em uma botnet.

Uma observação de CPU e rede de aproximadamente 157 segundos não confirmou um minerador ativo. A triagem de cadeias selecionadas em arquivos e assinaturas criptográficas válidas também não provam ausência de malware.

Os filtros DNS usam o nome em formato de labels DNS, com o zero terminal, `--algo kmp` e `--icase`. Isso cobre o domínio e subdomínios sem bloquear um domínio semelhante que apenas contenha aquele texto. As regras trabalham em pacotes: não reconstituem fluxos TCP nem inspecionam DoH/DoT.

## Validações executadas no aparelho

- Uma chave nova não autorizada foi rejeitada na etapa de autenticação; a chave existente continuou funcionando.
- Os testes de rede da etapa BADBOX rejeitaram 690 datagramas locais de teste, mantiveram 230 controles de nomes parecidos sem correspondência e validaram seis casos TCP. Também houve consultas ao resolvedor Android para os 115 nomes.
- A etapa final conferiu 58 condições após um reinício real: arquivos esperados, montagens somente leitura, regras preservadas, ausência de duplicação dos ganchos, autorizações, restrições e aplicativos.
- Uma conexão nova à porta IPv4 estável respondeu `STLS`, autenticou e executou manutenção antes e depois do reinício. A porta TLS interna mudou, e o redirecionamento acompanhou a mudança.
- A tentativa com usuário `shell` de executar `su` ou `run-as` passou a receber `Permission denied`; ADB root autorizado continuou disponível.
- Os 16 apps solicitados e a interface nova ficaram instalados e habilitados; os 27 pacotes removidos continuaram ausentes. O menu próprio do projetor abriu e Home retornou ao launcher.
- HTTPS de conectividade retornou 204. O perfil performance, limite original de CPU e proteção térmica permaneceram.

Esses testes no hardware se referem aos scripts instalados e às regras daquela sessão. Os utilitários Python publicados foram generalizados posteriormente e têm testes locais; não foram executados novamente no projetor após o encerramento do atendimento. Não confunda isso com compatibilidade comprovada em outra unidade.

Imagem e som do YouTube e de streaming local de um Switch haviam sido confirmados pelo proprietário em etapas anteriores. Reprodução física de HDMI, áudio, controle, AirPlay/Miracast e serviços pagos não foi toda repetida na etapa final. Inventário de pacotes não prova reprodução.

## Exceção de permissão e comportamento do framework

O app de mídia analisado recusava a abertura sem `READ_MEDIA_AUDIO`. Essa permissão original foi mantida; `MANAGE_EXTERNAL_STORAGE` e a solicitação de instalar outros APKs ficaram bloqueados por app-op.

O framework recompôs concessões legadas `READ_EXTERNAL_STORAGE`/`WRITE_EXTERNAL_STORAGE` depois do reinício. Não foram anunciadas como revogadas permanentemente. No app com alvo API 33, foram conferidos o isolamento de armazenamento e o bloqueio da operação de acesso amplo. Consulte a [documentação de permissões granulares](https://developer.android.com/about/versions/13/behavior-changes-13#granular-media-permissions).

## Limite da conclusão

O firmware permaneceu não confiável para uma conta principal: SELinux ausente, chaves de teste, patch antigo, integridade de boot sem garantia e manutenção root. O WebView não recebeu uma substituição sem compatibilidade e procedência comprovadas para esse provedor ARM de 32 bits. Um componente com root pode contornar controles locais.

O backup bruto foi mantido privado. Como foi capturado com Android em execução, não há prova de consistência offline de userdata; a restauração integral não foi ensaiada. Não é distribuído como imagem de recuperação ou firmware de terceiros.
