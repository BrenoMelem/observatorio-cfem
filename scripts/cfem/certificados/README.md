# Certificado intermediário da ANM

O servidor `dadosabertos.anm.gov.br` envia só o certificado dele, sem o intermediário. Por isso a validação falha em clientes que não completam a cadeia sozinhos (verificado em 08/11/2026: `unable to verify the first certificate`).

`sectigo-ov-r36.pem` é o intermediário "Sectigo Public Server Authentication CA OV R36" (emitido pela raiz R46, válido até 21/03/2036; SHA-256 `65:42:D1:76:BE:D5:0F:19:3C:0C:E2:97:AE:44:EC:D8:A0:A8:6B:EC:2E:DE:68:27:69:34:40:59:B4:E7:85:30`). Foi obtido pelo endereço que o próprio certificado indica (`CA Issuers`: `http://crt.sectigo.com/SectigoPublicServerAuthenticationCAOVR36.crt`) e a cadeia foi conferida contra as raízes do `certifi`. É certificado público. A verificação do servidor continua ligada; nunca desligue.

Se a ANM trocar de certificadora, o download falha com erro de certificado; refaça o procedimento acima.
