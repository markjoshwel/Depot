# Lotte Display Friend

a small macOS daemon that:

- has a system tray icon/status item for enabling and disabling the daemon
- checks a configurable amount of seconds to see if the display is being
  screen shared
- pings a configurable hostname to see if it's reachable
- and if said hostname is reachable, it will change the display mode to a
  preconfigured setting

## Rationale

i have a Mac mini i remotely access from my windows laptop. that laptop has a
resolution of 19200x1200 (16:10) versus other displays i use to access my mac,
which usually have 16:9 resolutions.

i have my desktop computing devices all under a Tailscale network, previously
for a minecraft server i hosted between me and my friends, but now I use for
taildrops (their file sharing feature) and the occasional cross-device network
communication, and the rarer ssh connection.

so the idea is, every few seconds, see if the display is being screen shared.
if it is, i want to ping my laptop to see if it's reachable. and if it is,
there is a good chance that i'm using my laptop as a remote display, and that
i would want the resolution to be changed to match my laptop's resolution.

## Prerequisites

- having a display mode which you want to change to \
  (use BetterDisplay to generate custom resolutions, or any other EDID-generating tool)

- having a hostname which you want to ping to trigger the display mode change \
  (as stated in my rationale, i use tailscale)
