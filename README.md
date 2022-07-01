# Social Info
Get info about the followers of another account. Works with Twitter, Instagram and TikTok.
Optionally output the data to a CSV with the following info...

```
# twitter csv headers
id,username,followers_count,following_count,tweet_count,listed_count,verified

# instagram csv headers
pk,username,full_name,is_private,profile_pic_url,profile_pic_id,is_verified,follow_friction_type,growth_friction_info,has_anonymous_profile_picture,has_highlight_reels,transparency_product_enabled,account_badges,latest_reel_media,reel_auto_archive,allowed_commenter_type,interop_messaging_user_fbid,fbid_v2,liked_clips_count,all_media_count,linked_fb_info,follower_count,following_count,mutual_followers_count,is_new_to_instagram

# tiktok csv headers
accept_private_policy,account_region,ad_cover_url,advance_feature_item_order,advanced_feature_info,apple_account,authority_status,avatar_168x168,avatar_300x300,avatar_larger,avatar_medium,avatar_thumb,avatar_uri,aweme_count,bind_phone,bold_fields,can_set_geofencing,cha_list,comment_filter_status,comment_setting,commerce_user_level,cover_url,create_time,custom_verify,cv_level,download_prompt_ts,download_setting,duet_setting,enterprise_verify_reason,events,favoriting_count,fb_expire_time,follow_status,follower_count,follower_status,followers_detail,following_count,geofencing,google_account,has_email,has_facebook_token,has_insights,has_orders,has_twitter_token,has_youtube_token,hide_search,homepage_bottom_toast,ins_id,is_ad_fake,is_block,is_discipline_member,is_phone_binded,is_star,item_list,language,live_agreement,live_commerce,live_verify,mention_status,mutual_relation_avatars,need_points,need_recommend,nickname,original_musician,platform_sync_info,prevent_download,react_setting,region,relative_users,room_id,search_highlight,sec_uid,secret,share_info,share_qrcode_uri,shield_comment_notice,shield_digg_notice,shield_follow_notice,short_id,show_image_bubble,signature,special_lock,status,stitch_setting,total_favorited,tw_expire_time,twitter_id,twitter_name,type_label,uid,unique_id,unique_id_modify_time,user_canceled,user_mode,user_period,user_rate,user_tags,verification_type,verify_info,video_icon,white_cover_url,with_commerce_entry,with_shop_entry,youtube_channel_id,youtube_channel_title,youtube_expire_time,room_data
```

## Requirements
Put your tokens in `env.example.secret` and rename that file to `env.secret` for the script.

- python3, pip
- RapidAPI token ([for TikTok](https://rapidapi.com/contact-cmWXEDTql/api/scraptik))
- Twitter Bearer Token
- Instagram username and password

## Usage
Install dependencies:
```bash
$ pip3 install -r requirements.txt
```

```bash
Usage:
    social_info.py instagram followers <user_id> [--inspect | --load-cursor] [<output.csv>]
    social_info.py twitter followers <user_id> [--inspect | --load-cursor] [<output.csv>]
    social_info.py tiktok followers <user_id> [--inspect | --load-cursor] [<output.csv>]
    social_info.py (-h | --help)

Options:
    --load-cursor       Load cursors from save data (recommended if you're picking up a previous session)
    -i --inspect        Show the available dictionary keys within a response (won't save output)
    -h --help           Show this message
```
