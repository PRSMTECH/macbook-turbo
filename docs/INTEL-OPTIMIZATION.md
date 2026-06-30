# Intel Mac Optimization Guide

MacBook Turbo includes optimizations tuned for **Intel Macs**, with special
handling for the famously throttle-prone **2018 15" MacBook Pro
(`MacBookPro15,1`, Core i9-8950HK)**.

## Why this matters on the 2018 i9

The 2018 15" MacBook Pro's chassis can't dissipate the i9's heat under sustained
load. The CPU (actually its VRM) hits thermal limits and **throttles — often
well below its base clock**. Apple shipped a thermal-management firmware fix in
July 2018, but the underlying physics remain: on this machine, **the bottleneck
is heat, not raw clock speed**.

The practical consequence is counter-intuitive: **capping peak heat usually
raises *sustained* performance** and quiets the fans, because the CPU stops
slamming into the throttle ceiling.

You can see live throttling at any time:

```bash
./scripts/optimize-intel.sh status
```

If `Speed limit` shows less than 100%, the CPU is being throttled *right now*.
The menu-bar app shows the same number under **⚡ Performance**, and adds a 🐢 to
the menu-bar title when throttling is heavy.

## The three levers

All of these are reversible with `./scripts/optimize-intel.sh revert`.

### 1. Disable Turbo Boost (biggest single win)

Turbo Boost briefly pushes clocks as high as 4.8 GHz — which is exactly what
triggers the throttle on this chassis. Disabling it can drop temperatures by up
to ~20 °C and *increase* sustained throughput.

macOS has no built-in switch, so this uses the free
[Turbo Boost Switcher](https://tbswitcher.rugarciap.com/) (a small kernel
extension that needs a one-time approval in **System Settings → Privacy &
Security**).

```bash
./scripts/optimize-intel.sh turbo-off    # disable
./scripts/optimize-intel.sh turbo-on     # re-enable
```

### 2. Force the integrated GPU

The 2018 i9 has both an Intel UHD 630 (integrated, cool) and a Radeon Pro 555X/
560X (discrete, hot). By default macOS switches automatically, and the discrete
GPU adds significant heat. Forcing the integrated GPU keeps the machine cooler.

```bash
./scripts/optimize-intel.sh gpu-integrated   # cooler (needs sudo)
./scripts/optimize-intel.sh gpu-auto         # restore automatic switching
```

### 3. Low Power Mode

macOS Low Power Mode lowers clocks and is an easy, fully-supported way to run
cooler and quieter (great on battery).

```bash
./scripts/optimize-intel.sh lowpower-on
./scripts/optimize-intel.sh lowpower-off
```

## One command to cool down

For a throttling i9, the fastest fix is the combined cool-down (integrated GPU +
Low Power Mode + Turbo Boost off):

```bash
./scripts/optimize-intel.sh cool-now
```

Undo everything:

```bash
./scripts/optimize-intel.sh revert
```

## UI speed tweaks (any Mac, no sudo)

Separately, you can make macOS *feel* snappier by trimming animation time. These
are per-user and fully reversible:

```bash
./scripts/macos-speed-tweaks.sh apply    # snappier UI + faster key repeat
./scripts/macos-speed-tweaks.sh revert   # restore macOS defaults
./scripts/macos-speed-tweaks.sh show     # show current values
```

## Hardware fixes (beyond software)

If the machine is years old, the largest remaining wins are physical:

- **Repaste the CPU/GPU** — degraded factory thermal paste is a major cause of
  throttling on aged 2018 units.
- **Clean dust** from the fans and exhaust.
- **Use a cooling pad / raise the rear** for better airflow.

## References

- [Apple: 2018 MacBook Pro thermal-management fix (9to5Mac)](https://9to5mac.com/2018/07/24/apple-releases-2018-macbook-pro-update-to-fix-cpu-throttling-thermal-management-bug/)
- [Round-up: user solutions for i9 throttling (AppleInsider)](https://appleinsider.com/articles/18/07/24/round-up-user-solutions-for-thermal-throttling-of-the-i9-2018-macbook-pro)
- [Turbo Boost Switcher](https://tbswitcher.rugarciap.com/)
- [Disable Turbo Boost to keep your MacBook cool (Cult of Mac)](https://www.cultofmac.com/how-to/disable-turbo-boost-keep-macbook-cool)
