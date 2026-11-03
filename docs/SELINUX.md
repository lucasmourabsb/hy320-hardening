# SELinux no kernel estudado

A configuração foi extraída de `/proc/config.gz` do kernel em execução, e não inferida apenas pela interface de configurações:

```text
CONFIG_SECURITY=y
# CONFIG_SECURITYFS is not set
# CONFIG_SECURITY_SELINUX is not set
```

`getenforce` retornou `Disabled`, e `selinuxfs` não apareceu entre os sistemas de arquivos suportados. Os argumentos de boot examinados não mostravam uma simples desativação por `selinux=0` ou `enforcing=0`.

Nessa compilação o mecanismo está ausente. `setenforce`, uma propriedade Android, um APK ou rótulos armazenados em arquivos não acrescentam o código ao kernel. A [definição do Linux 5.15](https://github.com/torvalds/linux/blob/v5.15/security/selinux/Kconfig) seleciona o recurso na compilação; os [LSMs não são módulos comuns carregáveis](https://docs.kernel.org/5.15/admin-guide/LSM/index.html).

É possível, em princípio, preservar a instalação Android e substituir a parte kernel/boot. Isso exigiria kernel e drivers compatíveis, além de inicialização, rótulos e [políticas de plataforma/fabricante](https://source.android.com/docs/security/features/selinux/build) corretos. Não foi construído ou gravado esse substituto no estudo.

SELinux pode coexistir com depuração autorizada em Android preparado para isso. A exigência de manter ADB ligado não é o motivo de ele faltar neste kernel. O obstáculo prático foi a necessidade de substituir componentes de boot sem uma recuperação independente testada: se Android ou Wi-Fi falhar, a conexão de manutenção desaparece.

Não foram forçados relock do bootloader, verity ou modo enforcing sobre uma política não validada. Os bloqueios e ajustes adicionais de permissões continuam sendo defesas parciais; eles não equivalem à proteção SELinux nem estabelecem confiança para uma conta importante.
