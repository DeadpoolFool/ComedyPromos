# comedypromos

Show and tour promo for @ARTEMISFUNNY: flyers, stories, reels, captions. One folder per show or run of shows, named `<slug>/`, with finished files in `<slug>/out/`.

## Whose look to use

- **A show or festival with its own branding:** keep their flyer, logos, colors and theme, and put Artem into it. The LBC flyer with his headshot (`lbc-fall-fest/out/lbc_flyer_feat_*`) is the model.
- **A tour, a lineup announcement, or a show with no branding of its own:** use Artem's theme below.

## Artem's theme

- Colors: black field, red `#df2731`, cream `#efe6d2`.
- Fonts: Anton (headlines), Space Mono (dates, handles, CTAs), Barlow Condensed (body).
- Logo: the pointing silhouette in `brand/logo_silhouette.png`, always top right, pointing at the show info.
- Handle `@ARTEMISFUNNY` bottom right. No footer bar needed.

## Rules for every flyer

- Times: show **seating**, 30 minutes before showtime, labelled SEATING. Make date, seating time and address big.
- Photos: real stage shots at real venues with the sign visible. Don't crop his body or the sign, and don't label the photos.
- CTA: "DM for tickets" or "Tickets: link in bio".
- Copy is written for fans who already know him, in his voice. Keep it pure comedy, with nothing about Arodus or finance, and don't over-explain the format or talk about the promo itself.
- Never invent show details (price, address, lineup, times). Get them from the confirmation email, the ticket page or the Comedy Workbook.

## Formats

| Use | Size |
|---|---|
| IG story | 1080×1920. Leave a clear band for the link sticker. |
| IG feed | 1080×1350. Use 1080×1080 for carousels, since 4:5 showed grey bars in his composer. |
| X header | 1500×500 |
| Business card | 85×55 mm, CMYK PDF (Flyeralarm) |

## Rendering

The scripts render HTML with headless Chromium (`/opt/pw-browsers/.../headless_shell`) and build reels with ffmpeg. Install the fonts first:

```bash
mkdir -p ~/.fonts
for f in anton/Anton-Regular.ttf spacemono/SpaceMono-Regular.ttf spacemono/SpaceMono-Bold.ttf \
         barlowcondensed/BarlowCondensed-Regular.ttf barlowcondensed/BarlowCondensed-Medium.ttf \
         barlowcondensed/BarlowCondensed-SemiBold.ttf barlowcondensed/BarlowCondensed-Bold.ttf; do
  curl -sfL "https://raw.githubusercontent.com/google/fonts/main/ofl/$f" -o ~/.fonts/$(basename $f)
done
fc-cache -f
```

A missing font falls back silently, so check `fc-list | grep -Ei "anton|space mono|barlow"` before rendering.

## Shows

| Folder | Show | Date |
|---|---|---|
| `lbc-fall-fest/` | Laughing Buddha Comedy Festival (LBC Fall Fest) prelim, The Buddha Room | Sat Oct 17, 2026 |
| `lbc-carousels/` | Photo carousels from the LBC Fall Fest prelim (Miguel's photos) | Oct 2026 |

Earlier promos (June to September 2026) were made in claude.ai chats and never saved to a repo. They include the LBC Industry Showcase poster (`brand/example_flyer_june_showcase.png`), the "It's Too Fucking Hot Tour" July poster, the "Final NYC shows before Deportation to Swissy Lands" flyer, the Rooftop 105 Geneva poster and story, the X header, and the KGB business cards.
