# HY320 Hardening

Auditoria e redução de exposição em projetores HY320 com Android, a partir de um estudo na variante **Amlogic `t950s_be311`**. Inclui ferramentas de leitura, geração local de bloqueios BADBOX/JM e os scripts de referência usados no aparelho estudado.

**Estado do projeto:** referência experimental validada em uma unidade, em 03/11/2026. O nome comercial HY320 é usado em placas e firmwares diferentes. Identifique sua variante antes de adaptar qualquer alteração.

## Comece pela leitura

É necessário Python 3.9+ e o [ADB oficial](https://developer.android.com/tools/releases/platform-tools). Use uma conexão já autorizada no seu aparelho.

```sh
python3 tools/audit.py --serial PROJECTOR_IP:5555
```

Se o servidor ADB estiver em outra porta:

```sh
python3 tools/audit.py --serial PROJECTOR_IP:5555 --server-port 5038
```

O comando consulta estado e configuração do kernel. Ele não instala apps, muda permissões, habilita root, reinicia o aparelho ou altera a depuração. O JSON é produzido por uma lista de campos permitidos; endereço de rede, MAC, serial, chave e contas não entram no relatório. Nenhuma conexão a serviços de terceiros é feita pelo programa.

## Conteúdo

| Diretório | Conteúdo |
| --- | --- |
| `tools/audit.py` | Leitura de segurança, SELinux, depuração e limites do kernel |
| `tools/render_blocklist.py` | Geração offline de regras DNS IPv4/IPv6 e entradas de hosts |
| `data/indicators.json` | 109 domínios BADBOX 2.0 e seis endpoints JM documentados |
| `android/` | Scripts de referência do estudo, que exigem revisão e root para instalação |
| `docs/ESTUDO.md` | Mudanças, validações e limitações observadas |
| `docs/ADAPTACAO.md` | Pré-condições, destinos dos arquivos e recuperação |
| `docs/SELINUX.md` | Por que SELinux não pôde ser ativado no kernel estudado |
| `docs/INTERFACE-E-APPS.md` | Launcher, limpeza e preservação dos recursos do projetor |

Para gerar os bloqueios, sem se conectar ao projetor:

```sh
python3 tools/render_blocklist.py --output generated
python3 -m unittest discover -s tests -v
```

`generated/hosts.include` é um trecho para revisão e mesclagem com o hosts existente. Não substitua o arquivo original indiscriminadamente. As regras mexem somente nas cadeias próprias `HY320_BB*` e `HY320_DNS*`; sua geração não instala os ganchos no firewall.

## Resultado do estudo

- Autenticação da manutenção com a chave do proprietário e conexão por TLS, mantendo a depuração ligada.
- Redirecionamento IPv4 da porta estável 5555 para o listener TLS dinâmico do Android, com teste após reiniciar.
- Restrição de caminhos extras de root, desativação de instalador/atualizador privilegiados sem uso e neutralização de rotinas de download remoto.
- Filtros de DNS por sufixo, hosts e um IP C2 documentado; regras do Android preservadas.
- Firewall de entrada e cinco ajustes do kernel, com persistência no reinício testado.
- Interface, 16 aplicativos solicitados, ajustes do projetor, performance e proteção térmica preservados.

Os payloads Android são publicados para inspeção e adaptação. Não há instalador universal ou comando de aplicação em massa. Os instaladores usados no atendimento original dependiam de backups privados, hashes e arquivos específicos daquela unidade, que não são distribuídos aqui.

## Limites de segurança

O firmware estudado continuou com patch declarado de abril de 2023, chaves de teste, integridade de boot sem garantia e kernel sem SELinux. A manutenção permaneceu root. **As mudanças não tornaram esse firmware confiável para uma conta Google principal ou de trabalho.**

Uma lista de indicadores não cobre servidores desconhecidos, todo DNS criptografado ou um processo comprometido com root. O modo de contingência da depuração é autenticado, mas sem TLS se o listener TLS não iniciar. A ausência de um minerador em uma amostra curta não comprova ausência de malware.

Backups, imagens de firmware, APKs, chaves, inventários privados e capturas do atendimento ficam fora do repositório. Informações de licença e referências estão em [NOTICE](NOTICE) e [docs/FONTES.md](docs/FONTES.md).

## Licença

O código original deste repositório está sob [MIT](LICENSE). Projetos citados mantêm suas próprias licenças. Este projeto não é afiliado aos fabricantes do HY320, ao Android, à HUMAN Security ou ao CleanYourTV.
