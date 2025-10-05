# Lotte Display Friend: screen sharing-based automatic resolution switcher

from ipaddress import IPv6Address, ip_address
from os import getpid as os_getpid
from socket import gaierror as socket_gaierror
from socket import gethostbyname as socket_gethostbyname
from subprocess import CompletedProcess, run
from sys import exit, stderr
from time import sleep
from typing import Final

LDF_LSOF_INVOCATION: Final[tuple[str, ...]] = (
    "lsof",
    "-nP",
    "-iUDP",
    "-a",
    "-c",
    "parsecd",
)
LDF_DETECT_PRESENT_INTERVAL: Final[float] = 2.0
LDF_DETECT_AWAY_INTERVAL: Final[float] = 6.0
LDF_PING_TARGET: Final[str] = "cspmilk"
LDF_PING_TIMEOUT: Final[float] = 5.0
LDF_DISPLAYPLACER_SCREENSHARING_MODE: Final[str] = (
    "id:BC5513CE-206D-4C47-BF1A-C5A1D02557C0 res:1920x1200 hz:60 color_depth:8 enabled:true scaling:off origin:(0,0) degree:0"
)
LDF_DISPLAYPLACER_NORMAL_MODE: Final[str] = (
    "id:BC5513CE-206D-4C47-BF1A-C5A1D02557C0 res:2560x1440 hz:60 color_depth:8 enabled:true scaling:off origin:(0,0) degree:0"
)

ldf_displayplacer_command: str = "/opt/homebrew/bin/displayplacer"

def _is_host_loopback(host: str) -> bool:
    host = host.strip()
    if not host:
        return False

    # bind-all (not loopback)
    if host in ("*", "0.0.0.0", "::"):
        return False

    # localhost (loopback)
    if (host.lower() == "localhost") or (host.lower() == "127.0.0.1"):
        return True

    # try parsing as literal ip address
    try:
        ip = ip_address(host)

    except ValueError:
        # if not (like in hostnames), assume it is not a loopback
        return False

    # handle ipv6
    if isinstance(ip, IPv6Address) and ip.ipv4_mapped is not None:
        return ip.ipv4_mapped.is_loopback

    return ip.is_loopback


def check_environment() -> bool:
    global ldf_displayplacer_command
    
    # try `displayplacer --help`
    cp_displayplacer_help: CompletedProcess[bytes] = run(
        [ldf_displayplacer_command, "--help"], capture_output=True
    )
    
    # if it fails, figure out where it is
    if cp_displayplacer_help.returncode != 0:
        cp_which: CompletedProcess[str] = run(
            ["which", "displayplacer"],
            capture_output=True,
            text=True
        )
        if cp_which.returncode != 0:
            print(
                "error: could not find the command `displayplacer`",
                file=stderr,
            )
            return False
        else:
            ldf_displayplacer_command = cp_which.stdout.strip()

    cp_lsof: CompletedProcess[bytes] = run(LDF_LSOF_INVOCATION, capture_output=True)
    if cp_lsof.returncode != 0:
        print(
            f"error: could not run the command `{' '.join(LDF_LSOF_INVOCATION)}`",
            file=stderr,
        )
        print(
            "stderr:",
            cp_lsof.stderr.decode(),
            sep="\n",
            file=stderr,
        )
        return False

    return True


def _check_if_screen_sharing() -> bool | None:
    cp_lsof = run(LDF_LSOF_INVOCATION, capture_output=True)
    if cp_lsof.returncode != 0:
        return None

    # parsecd   34806 majo   16u  IPv4 0x0000000000000000      0t0  UDP 127.0.0.1:5309
    # parsecd   34806 majo   28u  IPv6 0x0000000000000000      0t0  UDP *:21334

    for line in cp_lsof.stdout.decode().splitlines():
        # get the address at the end
        if not (
            # output format sanity check
            (len(sline := line.split()) == 9)
            # ensure last segment of output line is an address
            and (":" in sline[-1])
        ):
            continue

        # check if parsecd is connected to non-loopback address
        host, _ = sline[-1].split(":")
        if _is_host_loopback(host):
            print(
                f"debug: _check_if_screen_sharing: {host} identified as loopback",
                file=stderr,
            )
            continue

        # if it is connected to non-loopback address, then we are
        # screen sharing!
        print(
            f"debug: _check_if_screen_sharing: {host} identified as non-loopback",
            file=stderr,
        )
        return True

    return False


def _set_display_mode(is_screen_sharing: bool) -> None:
    display_mode = (
        LDF_DISPLAYPLACER_SCREENSHARING_MODE
        if is_screen_sharing
        else LDF_DISPLAYPLACER_NORMAL_MODE
    )

    cp_displayplacer = run(
        (
            ldf_displayplacer_command,
            display_mode,
        ),
        capture_output=True,
    )

    if cp_displayplacer.returncode != 0:
        print(
            f"error: could not set display mode via `{ldf_displayplacer_command} {display_mode}`",
            file=stderr,
        )
        print(
            "stderr:",
            cp_displayplacer.stderr.decode().strip(),
            sep="\n",
            file=stderr,
        )


def _ping_hostname(hostname: str) -> bool:
    # dns resolution
    resolved_hostname: str = "localhost"
    try:
        resolved_hostname = socket_gethostbyname(hostname)
    except socket_gaierror:
        return False

    print(
        f"debug: _ping_hostname: resolved `{hostname}` -> `{resolved_hostname}`",
        file=stderr,
    )

    # ping
    cp_ping = run(
        (
            "ping",  # god forbid ping isn't installed
            "-c",
            "1",
            resolved_hostname,
        ),
        capture_output=True,
    )

    # print("debug: _ping_hostname: ping returned", cp_ping.returncode, file=stderr)
    return cp_ping.returncode == 0


def core_loop() -> None:
    pid: Final[int] = os_getpid()
    is_screen_sharing: bool = False

    while True:
        print(
            f"lottedisplayfriend({pid}): status: "
            + f"{'screen sharing' if is_screen_sharing else 'not screen sharing'}\n",
            file=stderr,
        )
        sleep(
            LDF_DETECT_PRESENT_INTERVAL
            if (not is_screen_sharing)
            else LDF_DETECT_AWAY_INTERVAL
        )

        _old_screen_sharing_status = is_screen_sharing
        _current_screen_sharing_status = _check_if_screen_sharing()

        # set the current variable
        if _current_screen_sharing_status is not None:
            is_screen_sharing = _current_screen_sharing_status

        # check if we moved from not screen sharing to screen sharing
        if (
            _old_screen_sharing_status is False
            and _current_screen_sharing_status is True
        ):
            print(
                f"lottedisplayfriend({pid}): status state has changed, "
                + f"{_old_screen_sharing_status} -> {_current_screen_sharing_status}, "
                + f"pinging `{LDF_PING_TARGET}`",
                file=stderr,
            )
            if _ping_hostname(LDF_PING_TARGET):
                print(
                    f"lottedisplayfriend({pid}): ping success, setting display mode",
                    file=stderr,
                )
                _set_display_mode(is_screen_sharing)

        # else, check if the state changed anyways
        elif _old_screen_sharing_status != _current_screen_sharing_status:
            print(
                f"lottedisplayfriend({pid}): status state has changed, "
                + f"{_old_screen_sharing_status} -> {_current_screen_sharing_status}, "
                + "setting display mode",
                file=stderr,
            )
            _set_display_mode(is_screen_sharing)


def main():
    try:
        print("Lotte Display Friend - Python Testing ver.\n")

        if not check_environment():
            exit(1)

        print("lottedisplayfriend: initial display mode setting")
        initial_state = _check_if_screen_sharing()
        _set_display_mode(
            is_screen_sharing=(initial_state if initial_state is not None else False)
        )

        core_loop()

    except Exception as exc:
        print(f"error: {exc.__class__.__name__}: {exc}", file=stderr)
        exit(2)

    exit(0)


if __name__ == "__main__":
    main()
