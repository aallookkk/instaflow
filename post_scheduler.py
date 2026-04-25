"""
InstaFlow Post Scheduler
Runs via GitHub Actions every 15 minutes.
Reads queue.json, posts anything that's due, updates status.
"""

import os
import json
import time
import requests
from datetime import datetime, timezone

ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
ACCOUNT_ID = os.environ.get('INSTAGRAM_ACCOUNT_ID', '')
QUEUE_FILE = 'queue.json'
BASE_URL = f"https://graph.facebook.com/v19.0/{ACCOUNT_ID}"


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        print("No queue.json found. Nothing to post.")
        return []
    with open(QUEUE_FILE, 'r') as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)
    print(f"Saved queue.json with {len(queue)} items.")


def create_media_container(item):
    """Step 1: Create a media container on Instagram."""
    params = {
        'access_token': ACCESS_TOKEN,
        'caption': item.get('caption', ''),
    }
    post_type = item.get('type', item.get('post_type', 'IMAGE')).upper()

    if post_type == 'REELS':
        params['media_type'] = 'REELS'
        params['video_url'] = item.get('media_url') or item.get('mediaUrl')
        params['share_to_feed'] = 'true'
        cover = item.get('cover_url') or item.get('coverUrl')
        if cover:
            params['thumb_offset'] = '0'
    else:
        image_url = item.get('media_url') or item.get('mediaUrl')
        params['image_url'] = image_url

    response = requests.post(f"{BASE_URL}/media", params=params)
    data = response.json()

    if 'error' in data:
        print(f"  ❌ Container error: {data['error']['message']}")
        return None

    print(f"  ✅ Container created: {data['id']}")
    return data['id']


def wait_for_container(container_id, max_wait=60):
    """For Reels, wait until the container is FINISHED processing."""
    for i in range(max_wait // 5):
        r = requests.get(
            f"https://graph.facebook.com/v19.0/{container_id}",
            params={'fields': 'status_code', 'access_token': ACCESS_TOKEN}
        )
        status = r.json().get('status_code', '')
        print(f"  Container status: {status}")
        if status == 'FINISHED':
            return True
        if status == 'ERROR':
            return False
        time.sleep(5)
    return False


def publish_container(container_id, is_reel=False):
    """Step 2: Publish the container."""
    if is_reel:
        ready = wait_for_container(container_id)
        if not ready:
            print("  ❌ Container never finished processing.")
            return None

    response = requests.post(
        f"{BASE_URL}/media_publish",
        params={
            'creation_id': container_id,
            'access_token': ACCESS_TOKEN
        }
    )
    data = response.json()

    if 'error' in data:
        print(f"  ❌ Publish error: {data['error']['message']}")
        return None

    print(f"  ✅ Published! Post ID: {data.get('id')}")
    return data.get('id')


def post_item(item):
    """Full posting flow for one item."""
    media_url = item.get('media_url') or item.get('mediaUrl', '')
    post_type = item.get('type', item.get('post_type', 'IMAGE')).upper()
    label = item.get('label', 'Unnamed post')

    print(f"\n📤 Posting: {label} ({post_type})")
    print(f"   Media: {media_url[:60]}...")

    container_id = create_media_container(item)
    if not container_id:
        return False

    post_id = publish_container(container_id, is_reel=(post_type == 'REELS'))
    return post_id is not None


def main():
    if not ACCESS_TOKEN or not ACCOUNT_ID:
        print("❌ Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID secrets.")
        return

    now_ts = datetime.now(timezone.utc).timestamp()
    print(f"⏰ Checking queue at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    queue = load_queue()
    print(f"📋 Queue has {len(queue)} items.")

    changed = False
    for item in queue:
        if item.get('status') != 'scheduled':
            continue

        scheduled_ts = float(item.get('scheduled_ts', item.get('scheduledTs', 0)))
        if scheduled_ts <= 0:
            continue

        if scheduled_ts <= now_ts:
            success = post_item(item)
            item['status'] = 'posted' if success else 'failed'
            item['posted_at'] = datetime.now(timezone.utc).isoformat()
            changed = True
        else:
            remaining = scheduled_ts - now_ts
            print(f"  ⏳ '{item.get('label', '')}' scheduled in {int(remaining/60)} min")

    if changed:
        save_queue(queue)
        print("\n✅ Queue updated.")
    else:
        print("\n✅ No posts due right now.")


if __name__ == '__main__':
    main()
