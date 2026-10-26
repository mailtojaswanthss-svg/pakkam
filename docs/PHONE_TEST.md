# Phone test checklist (voice)

Try the mic on a real phone before recording the video. The browser only allows the
microphone on a secure page: `https://…` or `http://localhost`. A phone opening
`http://<laptop-ip>:8000` gets no mic, so use one of the two set-ups below.

## Before you start

- [ ] Lower the Gnani cap for the test: `SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY=20` in `.env`.
      Every mic question is 1 call and every Listen tap is 1 more.
- [ ] Start the server on the laptop: `uv run fastapi run` (port 8000).
- [ ] Check that `http://localhost:8000/chat/` works on the laptop first.

## Option A: Android, USB port forwarding (recommended, nothing is public)

1. On the phone, turn on Developer options, then USB debugging. Connect it by USB.
2. On the laptop, open `chrome://inspect/#devices` in Chrome.
3. Click **Port forwarding**, add `8000` → `localhost:8000`, tick **Enable port forwarding**.
4. On the phone, open Chrome at `http://localhost:8000/chat/`. Because it is localhost, the mic is allowed.

## Option B: HTTPS tunnel (needed for iPhone)

For example `cloudflared tunnel --url http://localhost:8000` or `ngrok http 8000`.
Either one prints an `https://…` address to open on the phone.

> **Warning.** A tunnel puts your laptop's server on the public internet. The server
> has no login, so anyone who finds the address can ask questions, which spends your
> LLM key, and use the mic and Listen, which spends Gnani credits (up to the daily
> cap). Don't share the address. **Close the tunnel (Ctrl+C) as soon as the test ends**,
> and put the daily cap back afterwards.

## What to check

- [ ] The language buttons are easy to tap. Tanglish shows "(being tested)".
- [ ] The first mic tap shows the browser's permission prompt. After you allow it, the timer counts "● 0:01 / 0:30".
- [ ] The Stop square and ✕ Cancel both work. Cancel sends nothing, so the call count doesn't change.
- [ ] Let one recording run: "5 seconds left" appears at 0:25 and it sends itself at 0:30.
- [ ] Ask one short question in each language you plan to show. Check "Pakkam heard:" against what you said.
- [ ] Block the mic in site settings and reload: "Mic is off. Type instead…" appears.
- [ ] Turn on airplane mode just after tapping Stop: "Send again" appears, and after you turn it off, it resends the same clip.
- [ ] Listen (only if TTS is switched on) plays, and Stop stops it.
- [ ] Rotate the phone and try with the on-screen keyboard open: the mic and Send stay reachable.

## iPhone Safari: known risks (untested)

- **Audio may need to start on the tap.** Safari can leave an `AudioContext` paused
  unless it starts inside the tap itself. The recorder creates it after the mic
  permission prompt, so on iPhone the clip may come out silent and Pakkam will say it
  could not hear you. If that happens, tell me: the fix is to create or resume the
  `AudioContext` straight away when the mic is tapped.
- **Sample rate.** iPhones usually record at 48 kHz, which the recorder brings down
  to 16 kHz. If the phone gives a rate below 16 kHz (some Bluetooth headsets do), the
  file would be labelled with the wrong rate and sound too fast. Test with the
  phone's own mic, not a headset.
- **Listen playback** may need a second tap the first time, because of Safari's autoplay rules.
- Silent mode on the iPhone can mute Listen. Check the ringer switch.

## After the test

- [ ] Close the tunnel or turn off port forwarding.
- [ ] Put `SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY` back.
- [ ] Note the credits used (from the Gnani dashboard) and any problems in STATUS.md.
- [ ] Don't keep test recordings. The app doesn't save audio, but delete any screen recordings that contain other people's voices.
