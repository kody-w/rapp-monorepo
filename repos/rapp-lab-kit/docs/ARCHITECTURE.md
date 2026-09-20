# Architecture notes

Findings that cost real time. Each is a constraint, not a preference.

## macOS TCC forbids launchd agents from network volumes

The monitor originally wrote samples to an SMB share. It worked from Terminal
and failed under `launchd` with `Operation not permitted`. Isolated with a bare
LaunchAgent doing nothing but touching the share:

```
ls   : DENIED
write: DENIED
```

Same script, same user, same mount — Terminal succeeds because it carries a TCC
grant the agent does not inherit. This affects **every** Mac, so SMB is the wrong
transport for unattended collection. Probes POST over HTTP instead: no
credentials, no per-machine Full Disk Access grant.

## Never derive a filename from the server clock

QNAP runs PHP in `Asia/Taipei`. `api.php` computed today's filename with
`date('Y-m-d')`, looked for tomorrow's file, and returned zero rows while ingest
was plainly writing. It now globs the directory. The day of a sample comes from
the **probe's own timestamp**, never the server's.

## Measure what hurts, not what is easy

Bandwidth is the easy number and the wrong one. **Jitter** decides call quality:
under 15 ms healthy, over 30 ms breaks calls. Worth separating two loads — a
saturating transfer is a stress test, while ~4 Mbps up is what a video call
actually does, and a link can pass one and fail the other.

## Kill the process group, not the shell

A `p.kill()` on a `shell=True` Popen reaps `/bin/sh` and orphans the `curl`
behind the pipe. Successive measurement rounds then stack concurrent uploads and
the numbers inflate run over run — the harness reports congestion it created
itself. Start the child with `start_new_session=True`, kill the group, and
refuse to measure while a stray transfer is still alive.

## QNAP specifics

- Container Station's docker listens on `unix:///var/run/system-docker.sock`,
  **not** `/var/run/docker.sock`. Binary at `<vol>/.qpkg/container-station/bin/docker`.
- busybox has no `nohup`; detach with `( setsid cmd & )`.
- SSH needs the "Allow SSH" toggle **and** the user ticked in *Edit Access
  Permission*, **and** a home folder (Privilege → Users → Home Folders) or
  `ssh-copy-id` fails with `can't create directory '.ssh'`.
- Files written by the web server are not writable over SMB — edit via SSH.

## Retention lives in the app, not cron

QNAP wipes `/etc/config/crontab` on firmware updates, so a cron job would
silently stop and nothing would say so. `ingest.php` prunes on roughly 1 request
in 50 instead.
