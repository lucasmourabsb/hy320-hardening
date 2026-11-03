# Fontes e atribuições

Os resultados de execução são do estudo na unidade descrita em [ESTUDO.md](ESTUDO.md). Estas referências explicam indicadores e mecanismos; nenhuma delas valida automaticamente este aparelho ou endossa o projeto.

- [HUMAN Security — BADBOX 2.0](https://www.humansecurity.com/learn/blog/satori-threat-intelligence-disruption-badbox-2-0/): origem dos 109 domínios C2 da lista inicial.
- [cleanyourprojector — JM firmware backdoor](https://github.com/tqhit/cleanyourprojector/blob/main/docs/JM-FIRMWARE-BACKDOOR.md): pesquisa pública da família JM e infraestrutura relacionada. Relação com uma cadeia observada em pesquisa não comprova contato ativo por esta unidade.
- [CleanYourTV](https://github.com/Gathin23/cleanyourtv): projeto original de limpeza/interface consultado. Seu código e sua licença não são incorporados neste repositório.
- [ADB Wi-Fi — arquitetura oficial](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/dev/adb_wifi.md): autenticação, listener TLS e diferenças do transporte clássico.
- [Linux 5.15 — LSM](https://docs.kernel.org/5.15/admin-guide/LSM/index.html) e [Kconfig SELinux](https://github.com/torvalds/linux/blob/v5.15/security/selinux/Kconfig).
- [Linux — sysctl fs](https://docs.kernel.org/admin-guide/sysctl/fs.html) e [sysctl kernel](https://docs.kernel.org/admin-guide/sysctl/kernel.html): proteções de links, arquivos, FIFOs e logs.
- [AOSP — política SELinux](https://source.android.com/docs/security/features/selinux/build), [Verified Boot](https://source.android.com/docs/security/features/verifiedboot) e [assinaturas de produção](https://source.android.com/docs/core/ota/sign_builds).
- [Android 13 — permissões granulares de mídia](https://developer.android.com/about/versions/13/behavior-changes-13#granular-media-permissions).
- [WebView AOSP](https://android.googlesource.com/platform/external/chromium-webview/+/refs/heads/main/) e [Cromite](https://github.com/uazo/cromite/blob/master/README.md): referências consultadas para compatibilidade de provedor e arquitetura.

A lista em `data/indicators.json` é um snapshot revisado em 03/11/2026. Não é um feed atualizado automaticamente, e não houve reprodução de artigos completos ou incorporação de APKs/firmware de terceiros.
