# Rapp Hive Support

Rapp Hive is a voice-first mirror for the RAPP Brainstem you run yourself, for iPhone. This first release is the **Founders Edition**, and every feature is free.

- [Rapp Hive on the App Store](https://apps.apple.com/app/id6816163757)
- [Privacy policy](PRIVACY.md)

## What do I need?

A RAPP Brainstem that you run yourself — on this computer, your network, or
reached through a RAPP Mirror. Rapp Hive talks to it and to nothing else.

## How do I connect from my phone?

The easiest way is to **link your RAPP Mirror**: in the Mirror, press the phone
button (**Link a phone**), then in Rapp Hive open **Herd › Scan pairing code**.
The phone then reaches your brainstem through the Mirror, with no secret to
copy.

To reach a brainstem directly instead, start it with `BRAINSTEM_LAN_MODE=true`,
then in **Settings** enter `http://<your computer's address>:7071` and paste the
secret from `~/.brainstem/src/rapp_brainstem/.brainstem_secret` on that
computer. The secret stays in this device's keychain and is sent only to the
address it was saved for.

## Why does it say my brainstem is locked?

Your brainstem answered but won't accept requests from this device without its
secret. Link your Mirror, or add the secret in **Settings**.

## Can Rapp Hive install agents?

No. Agent cards are previews for consent: scanning or tapping a shared card
shows a review card, and nothing is installed. Add agents from your desktop RAPP
Mirror.

## How do I share a card?

Open any card full screen and tap **Share card**. The share sheet sends a
picture of the side that is showing, the card's name and verdict, and a link to
get Rapp Hive, to whoever you choose, in Messages or any other app. A recipe
card also carries its `rapp://agent` link on its own line, so a friend's Rapp
Hive, Mirror, or AI can pick it up. Live agents are real Python, so only their
picture travels, never their code.

## How do I become a founder?

This first release is the **Founders Edition**, and every feature is free. Tap
**Settings › Become a founder › Contact us**, or email the address below with
the subject "Rapp Hive founder". Founders are grandfathered in when paid plans
arrive, and get a founder badge for their app and their AI, the Founders Club on
Discord, and a weekly email on new features, the roadmap, and what we learn
building AI.

## What can a linked phone do to my Mirror?

What a local AI can: choose portals, talk to the Mirror, start and prompt agents
in its Herd, and answer what they ask. Anything consequential follows the
**Autopilot** switch in your Herd, which only you can change, at the Mirror. The
camera, screen, microphone, pairing, and the Autopilot switch never leave the
Mirror. Unlink the phone from **Settings** here, or from **Link a phone** there.

## Does voice leave my phone?

Speech recognition runs on your device when it supports it; otherwise your
platform's speech service processes it. Only the resulting text is sent to your
brainstem.

## How do I remove my data?

**Settings › Erase all data** removes the saved address, secret, Mirror link,
and preferences from this device and clears the conversation. Your brainstem and
Mirror are not touched.

## Contact

Email [wildfeuer05@gmail.com](mailto:wildfeuer05@gmail.com), or open an issue at
<https://github.com/kody-w/rapp-hive-app/issues>.
