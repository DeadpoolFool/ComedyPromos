# comedypromos

Show and tour promo for @ARTEMISFUNNY: flyers, stories, reels, captions. One folder per show or run of shows, named `<slug>/`, with finished files in `<slug>/out/`.

## Brand rules

These come from past flyers and from corrections Artem has made. Follow them unless he says otherwise.

- Colors: black field, red `#df2731`, cream `#efe6d2`. When the show belongs to someone else's brand (Eventfrog, HACPAC, a producer's template), match their palette instead.
- Fonts: Anton (headlines), Space Mono (dates, handles, CTAs), Barlow Condensed (body).
- Logo: the pointing silhouette in `brand/logo_silhouette.png`, always top right, pointing at the show info. Fine print "look down there dummy" where there's room.
- Times: show **seating**, 30 minutes before showtime, labelled SEATING. Make date, seating time and address big.
- Photos: real stage shots at real venues with the sign visible. Don't crop his body or the sign, and don't label the photos.
- Handle `@ARTEMISFUNNY` bottom right. No footer bar needed.
- CTA: "DM for tickets" when he wants to know who's coming, or "Tickets: link in bio".
- Copy is for fans who already know him, written in his voice. Keep it pure comedy, with nothing about Arodus or finance.
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

Earlier promos (June to September 2026) were made in claude.ai chats and never saved to a repo. They include the LBC Industry Showcase poster (`brand/example_flyer_june_showcase.png`), the "It's Too Fucking Hot Tour" July poster, the "Final NYC shows before Deportation to Swissy Lands" flyer, the Rooftop 105 Geneva poster and story, the X header, and the KGB business cards.
