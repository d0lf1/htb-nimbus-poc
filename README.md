# HTB · Nimbus — PoC

Proof-of-concept per la macchina **Nimbus** (Hack The Box, Season 11).
Writeup completo: https://blog.ldsec.it/nimbus/

**Catena:** SSRF nell'anteprima job → leak credenziali IMDS → RCE via SQS/YAML →
foothold → credenziali AWS nell'env → build CodeBuild privilegiata →
`modprobe` hijack → root.

| File | Ruolo |
|------|-------|
| `ssrf.py` | PoC della SSRF verso l'IMDS per il leak delle credenziali |
| `exploit.py` | Catena di sfruttamento SQS/YAML → RCE |
| `probe.py` | Enumerazione/ricognizione dell'ambiente cloud |
| `script.sh` | Buildspec CodeBuild + write su `/proc/sys/kernel/modprobe` |
| `modprobe_cb_exploit.sh` | Privesc via modprobe hijack attraverso CodeBuild |
| `payload.sh`, `shell.sh` | Payload / reverse shell di supporto |

> Le credenziali AWS presenti negli script sono quelle del lab (LocalStack), non reali.
> ⚠️ Solo a scopo educativo e per testing autorizzato.

## Licenza e uso autorizzato

Distribuito sotto licenza [MIT](LICENSE).

Codice proof-of-concept pubblicato a scopo educativo e di ricerca, come
companion dei writeup su <https://blog.ldsec.it>. Sviluppato ed eseguito
esclusivamente contro una macchina di laboratorio volutamente vulnerabile, in
un contesto isolato e autorizzato. Usalo solo su sistemi di cui sei proprietario
o per i quali hai un'autorizzazione esplicita a eseguire test di sicurezza.
