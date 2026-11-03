# Adaptação e recuperação

## Ferramentas de leitura e payloads têm escopos diferentes

`tools/audit.py` faz consultas por ADB. `tools/render_blocklist.py` gera arquivos locais. Eles não instalam os scripts de `android/`.

Os payloads usam root, init e firewall do Android. A referência testada pressupõe uma variante conhecida, autenticação ADB já funcionando, chave do proprietário autorizada e overlays existentes de `/system` e `/vendor`. O projeto não ensina a obter root, desbloquear bootloader ou desativar verificação de imagens para atender a esses pré-requisitos.

Instalar os payloads depende de conhecer os arquivos de inicialização daquela placa e preservar sua recuperação. Não se deve aplicar uma lista de remoção ou substituir init de outro HY320 só pelo modelo comercial.

## Mapeamento de arquivos da referência

| Arquivo no repositório | Destino usado no estudo |
| --- | --- |
| `android/badbox-guard.sh` | `/system/bin/hy320-badbox-guard.sh` |
| `android/badbox-guard.rc` | `/system/etc/init/hy320-badbox-guard.rc` |
| `generated/badbox-v4.rules` | `/system/etc/hy320-badbox-v4.rules` |
| `generated/badbox-v6.rules` | `/system/etc/hy320-badbox-v6.rules` |
| `android/security-guard.sh` | `/system/bin/hy320-security-guard.sh` |
| `android/security-guard.rc` | `/system/etc/init/hy320-security-guard.rc` |
| `android/input-v4.rules` | `/system/etc/hy320-input-v4.rules` |
| `android/input-v6.rules.in` | `/system/etc/hy320-input-v6.rules` |

Scripts shell eram `0755`; arquivos `.rc` e regras, `0644`, com dono root. Contextos foram preservados/repostos e as montagens retornaram a somente leitura. Os scripts de neutralização em `android/` são conteúdo de substituição para caminhos legados que foram individualmente identificados, copiados e verificados; não são uma lista de alvos universais.

O arquivo IPv6 `.in` é um fragmento deliberadamente sem `COMMIT`. O guard acrescenta prefixos locais, o descarte final e `COMMIT` antes de validá-lo com `ip6tables-restore --test`. Não aplique o fragmento diretamente.

O gerador publicado explicita `-F` somente nas cadeias próprias. Isso mantém a intenção das regras do estudo sem depender do comportamento de redefinição de cadeias de uma versão específica de iptables-restore. As regras geradas precisam passar pelo parser/kernel do dispositivo; testes locais não verificam extensões do seu iptables.

## ADB com TLS e porta estável

O `security-guard.sh` usa o listener TLS nativo do Android, mantém `adb_enabled` e preserva autorizações existentes. Ele **não ativa autenticação RSA nem cadastra chaves**: `ro.adb.secure=1` e a autorização do host precisam estar previamente conferidos.

Quando a porta TLS está publicada e escutando, uma cadeia NAT própria redireciona novas conexões IPv4 recebidas em `wlan0:5555`. O filtro bloqueia acesso remoto bruto à porta legada, preservando loopback e sessões estabelecidas. A interface `wlan0` é específica da referência. A alteração de interface precisa ser revisada também no gancho e na contingência.

No kernel estudado não havia NAT IPv6. Portanto o acesso remoto bruto IPv6 à porta 5555 foi bloqueado; o endereço de manutenção estável testado era IPv4. As regras não prometem suporte a todas as topologias ou redes IPv6 futuras.

Se o listener TLS não surgir no prazo, o script mantém manutenção clássica autenticada na rede local e informa `authenticated-legacy-fallback`. Essa contingência preserva acesso, mas é sem criptografia. `tls` em uma propriedade, sozinho, não prova o transporte: o estudo testou saudação `STLS` e conexão autenticada nova.

O `adbd` continuou root. Retirar SUID/permissão de grupo de `su` e `run-as` ao mesmo tempo que se reduz o ADB a um usuário sem privilégio pode eliminar o caminho de manutenção. A referência não fez essa combinação.

## Firewall e inicialização

São usadas somente cadeias próprias e `--noflush`; as cadeias normais do Android devem permanecer intactas. Os serviços init são `oneshot`, acionados em eventos de inicialização e rede. Eles terminam depois de configurar as restrições.

O firewall de entrada permite redes privadas/locais, respostas a conexões existentes e mensagens essenciais de rede. Não isola aparelhos dentro da mesma LAN. Prefixos globais IPv6 diretamente conectados são coletados no momento em que o guard executa; uma mudança posterior de rede pode exigir reaplicação revisada. Se netd ou outro firewall reescrever regras, verifique os ganchos novamente.

## Processo usado no estudo

1. Copiar os originais, metadados e hashes para um computador e verificar as cópias.
2. Conferir modelo real, root, chave autorizada e sessão de manutenção existente.
3. Validar sintaxe shell e o parser de regras antes de instalar ganchos.
4. Alterar apenas os arquivos identificados no overlay já existente, com substituição atômica; devolver a montagem a somente leitura.
5. Manter uma sessão aberta enquanto outro servidor ADB verifica uma conexão nova. Não remover o único acesso antes desse teste.
6. Verificar os recursos necessários e um reinício real, sem acionar manualmente os guards para simular persistência.

O estudo não fornece garantia de recuperação fora do Android. Gravar boot/kernel/ROM apenas por Wi-Fi foi abandonado porque um boot malsucedido elimina esse acesso. Um backup sem restauração independente testada não resolve esse problema.

## Reversão

Uma reversão específica precisa remover apenas os ganchos e cadeias próprios, restaurar os arquivos e estados efetivamente guardados para aquela unidade e preservar sua chave ADB. Ao desfazer TLS, reconecte pelo transporte de recuperação antes de desligar o listener ativo. Não use flush global de iptables e não restaure arquivos de outra placa.

Os backups do proprietário e os instaladores privados que dependiam deles não são distribuídos. Esse é o motivo de os payloads terem aplicação manual revisada, e não um instalador genérico.
