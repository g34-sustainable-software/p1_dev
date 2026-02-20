
import asyncio
import argparse
import random
import os
from playwright.async_api import async_playwright

VIDEO_URL = "https://www.youtube.com/watch?v=d4u4cgxTShU"  # up to 4k, no ads
EXPERIMENT_DURATION = 30  # how long the video should play in the experiment (in seconds)

SETTINGS = ["all-off", "stable-volume", "voice-boost", "ambient-mode"]

"""
Under target/release add the energibridge executable (cargo build --release) so we can call the command

Example run:
python run_experiment.py --setting ambient-mode
or
python run_experiment.py --setting all-off stable-volume voice-boost ambient-mode
"""


async def run_all_iterations(settings: list[str]):
    settings_list = []
    for s in settings:
        settings_list.extend([s] * 3)  # this is only 3 for testing, should be 30 # TODO

    random.shuffle(settings_list)

    print("Settings are: " + str(settings_list))

    for i, s in enumerate(settings_list, start=1):
        output_file = f"./results/{s}/run_{i:02d}.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        print(f"\n=== Run {i} | Setting: {s} ===")
        await run_experiment(s, output_file)
        print(f"\n=== Finished, sleeping in between ===")
        await asyncio.sleep(10) # should ne 30 TODO


async def run_experiment(setting: str, output_file: str):
    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=False,
        channel="chrome",
        args=[
            "--autoplay-policy=no-user-gesture-required",
            "--incognito",
            "--disable-blink-features=AutomationControlled",
        ],
    )

    context = await browser.new_context(
        viewport={"width": 1512, "height": 982},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    )

    # dark mode needed for ambient mode
    await context.add_cookies([{
        "name": "PREF",
        "value": "tz=Europe.Amsterdam&f6=400",
        "domain": ".youtube.com",
        "path": "/",
    }])

    page = await context.new_page()
    print("Browser ready")

    await page.goto(VIDEO_URL, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    # accept cookies
    try:
        await page.click('button:has-text("Accept all")', timeout=5000)
        await page.wait_for_timeout(1000)
    except Exception:
        pass

    # make sure the cookies were accepted
    try:
        await page.wait_for_selector('ytd-consent-bump-v2-lightbox', state='hidden', timeout=5000)
    except Exception:
        pass  # no overlay, continue

    # pause the video
    try:
        await page.click('button.ytp-play-button', timeout=5000)
    except Exception:
        pass

    await page.wait_for_timeout(3000)
    print("Video loaded")

    # apply settings
    await apply_settings(page, setting)
    print(f"Setting set to: {setting}")

    # make sure video is playing
    play_btn = page.locator('button.ytp-play-button')
    aria_label = await play_btn.get_attribute('aria-label')
    if aria_label and 'Play' in aria_label:
        await play_btn.click()
    await page.wait_for_timeout(3000)

    print("Playing... -> Ready to start measuring!!")

    # measurement
    print(f"Measuring {EXPERIMENT_DURATION}s at setting '{setting}'...")
    await start_energibridge(output_file)

    print("Measurement done.")

    # close the browser
    await browser.close()
    await playwright.stop()

    print("Browser closed")


async def toggle_setting(page, label: str, enable: bool):

    menu_item = page.locator(f'div.ytp-menuitem:has(div.ytp-menuitem-label:has-text("{label}"))')
    await menu_item.wait_for(state="visible", timeout=10000)

    is_checked = await menu_item.get_attribute('aria-checked')
    currently_on = is_checked == 'true'

    if enable != currently_on:
        print(f"{'Enabling' if enable else 'Disabling'} '{label}'")
        await menu_item.click()
        await page.wait_for_timeout(500)
    else:
        print(f"'{label}' already {'on' if currently_on else 'off'}, skipping")


async def apply_settings(page, setting: str):

    await page.mouse.move(960, 540)
    await page.wait_for_timeout(500)
    settings_btn = page.locator('button.ytp-settings-button')
    await settings_btn.wait_for(state="visible", timeout=10000)
    await settings_btn.click()
    await page.wait_for_timeout(1000)

    menu = page.locator('div.ytp-settings-menu')
    await menu.wait_for(state="visible", timeout=10000)

    # set each setting individually to a needed value
    await toggle_setting(page, "Stable Volume", setting == "stable-volume")
    await toggle_setting(page, "Voice Boost", setting == "voice-boost")
    await toggle_setting(page, "Ambient Mode", setting == "ambient-mode")

    # Close menu when done
    await page.keyboard.press('Escape')
    await menu.wait_for(state="hidden", timeout=5000)
    await page.wait_for_timeout(500)

async def start_energibridge(output: str):
    print("Starting energibridge.")
    process = await asyncio.create_subprocess_exec(
        "target/release/energibridge",
        "-o", output,
        "--summary",
        "sleep", str(EXPERIMENT_DURATION)
    )
    await process.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", nargs="+", choices=SETTINGS, required=True,
                        help=f"One or more settings to test: {SETTINGS}")
    args = parser.parse_args()
    asyncio.run(run_all_iterations(args.settings))