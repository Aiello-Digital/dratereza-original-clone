# Dra. Tereza Barbosa — Landing Page

Redesign do site institucional, criado via Landing Page Builder (Claude AI) para a Aiello Digital.
Substitui o site WordPress anterior (tema Enfold), corrigindo os pontos de performance, SEO e conversão levantados em auditoria.

## Stack
HTML5 + CSS3 + JavaScript vanilla. Sem dependências, sem build. Pronto para deploy no Vercel.

## Arquivos
- `index.html` — página única com todo o conteúdo
- `styles.css` — sistema de design (variáveis em `:root`)
- `script.js` — scroll reveal, menu mobile, acordeão do FAQ
- `assets/` — logo e fotos reais reaproveitadas do site atual (`dratereza.com.br`)
- `vercel.json` — headers de segurança para o Vercel

## O que foi corrigido em relação ao site anterior
- **Banner de cookies removido**: a página não usa cookies não-essenciais (sem GTM/GA por enquanto), então não há bloqueio de CTA no mobile. Se um GTM/GA for adicionado depois, reintroduzir um banner de consentimento é necessário.
- **H1 único**: "Dra. Tereza Barbosa — Pediatra Homeopata" (antes eram dois H1 separados: "Pediatra" / "Homeopata").
- **Schema.org**: adicionado `Physician` (com endereço, geo, telefone, especialidade) e `FAQPage` — ausentes no site anterior.
- **Fontes**: Google Fonts (Fraunces + Inter) via `display=swap`, sem arquivos `.woff` pesados customizados.
- **Sem scripts de mídia desnecessários** (mediaelement/jQuery do WordPress removidos — não há vídeo na página).
- **Imagens** com `loading="lazy"` (exceto hero) e `alt` descritivo único por imagem.
- **WhatsApp**: botão fixo (flutuante) + botão no header + CTAs ao longo da página, todos com mensagem pré-preenchida.
- **Prova social**: seção estruturada e pronta, sem depoimentos fabricados — ver abaixo.

## Prova social / depoimentos
A seção `#depoimentos` está com um placeholder textual (sem inventar avaliações). Assim que a Dra. Tereza enviar depoimentos reais de pacientes (texto + nome, WhatsApp, Google ou Instagram), substituir o bloco `.testimonial-placeholder` em `index.html` por cards de depoimento (ver `references/copy-templates.md` do skill para o formato de card, se necessário).

## Mapa
Embed padrão do Google Maps via URL de busca pelo endereço (não requer chave de API). Caso se prefira o embed oficial "Compartilhar > Incorporar mapa" do Google, é só trocar o `src` do iframe em `#localizacao`.

## Deploy no Vercel
1. Importe este repositório no Vercel (vercel.com/new)
2. Sem configuração adicional — clique em Deploy
3. Em Settings > Domains, adicione `dratereza.com.br` e `www.dratereza.com.br`

## Apontamento de DNS
Após o deploy:
- **Domínio raiz**: registro `A` → `76.76.21.21`
- **www**: registro `CNAME` → `cname.vercel-dns.com`
- SSL configurado automaticamente pelo Vercel após propagação (até 48h)

## Sugestões de integração futura
- [ ] Google Tag Manager / GA4 — cliente não forneceu código nesta rodada; adicionar quando disponível (reintroduzir aviso de cookies ao ativar)
- [ ] Avaliações do Google como widget ao vivo (Elfsight ou Places API) — hoje a seção só linka para o perfil no Google Maps
- [ ] Facebook Pixel — o site anterior já rodava Google Ads (conversão `AW-1012406323`); confirmar com a cliente se quer recriar rastreamento de conversão
- [ ] Formulário de contato (hoje o único canal é WhatsApp/telefone, por escolha da cliente)

## Editando conteúdo
- **Textos**: diretamente no `index.html`, organizado por seção com IDs (`#hero`, `#atendimento`, `#fases`, `#experiencia`, `#depoimentos`, `#consultorio`, `#localizacao`, `#faq`)
- **Cores**: variáveis no topo do `styles.css`, em `:root { }`
- **Logo/fotos**: substituir os arquivos correspondentes em `assets/`
